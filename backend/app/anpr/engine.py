import os
import time
import cv2
import numpy as np
import onnxruntime as ort
from typing import Optional, List, Tuple
from app.anpr.schemas import PlateOCRResult
from app.anpr.normalizer import IndianPlateNormalizer
from app.anpr.validator import IndianPlateValidator

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
DEFAULT_MODEL_PATH = os.path.join(MODEL_DIR, "en_PP-OCRv4_rec_infer.onnx")
DEFAULT_DICT_PATH = os.path.join(MODEL_DIR, "en_dict.txt")


class PlateOCREngine:
    """
    Production ONNX-PP-OCRv4 Character Recognition Engine.
    Executes deep convolutional-recurrent CTC inference on CPU using ONNX Runtime.
    """

    _session: Optional[ort.InferenceSession] = None
    _character_list: Optional[List[str]] = None

    def __init__(
        self,
        model_path: str = DEFAULT_MODEL_PATH,
        dict_path: str = DEFAULT_DICT_PATH
    ):
        self.model_path = model_path
        self.dict_path = dict_path
        self.normalizer = IndianPlateNormalizer()
        self.validator = IndianPlateValidator()
        self.engine_name = "ONNX-PP-OCRv4"
        self.engine_version = "ppocr_v4_onnx"
        self._ensure_loaded()

    def _ensure_loaded(self):
        """Initializes ONNX Runtime InferenceSession with CPUExecutionProvider."""
        if PlateOCREngine._session is None:
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"ONNX Model file not found at: {self.model_path}")

            # Session options for multi-threaded edge CPU inference
            opts = ort.SessionOptions()
            opts.intra_op_num_threads = 2
            opts.inter_op_num_threads = 1
            opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL

            PlateOCREngine._session = ort.InferenceSession(
                self.model_path,
                sess_options=opts,
                providers=["CPUExecutionProvider"]
            )

        if PlateOCREngine._character_list is None:
            if os.path.exists(self.dict_path):
                with open(self.dict_path, "r", encoding="utf-8") as f:
                    dict_chars = [line.strip("\r\n") for line in f.readlines()]
                PlateOCREngine._character_list = ["blank"] + dict_chars + [" "]
            else:
                chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~ "
                PlateOCREngine._character_list = ["blank"] + list(chars) + [" "]

    def recognize_plate(
        self,
        plate_crop_bgr: np.ndarray,
        plate_quality: float = 0.85
    ) -> PlateOCRResult:
        """
        Executes ONNX neural inference over a localized license plate crop.
        """
        start_time = time.perf_counter()

        if plate_crop_bgr is None or plate_crop_bgr.size == 0 or plate_quality < 0.25:
            return PlateOCRResult(
                raw_text="",
                normalized_plate=None,
                ocr_confidence=0.0,
                format_valid=False,
                final_confidence=0.0,
                readability="UNREADABLE",
                components=None,
                ocr_engine=self.engine_name,
                engine_version=self.engine_version,
                ocr_latency_ms=0.0
            )

        # 1. Preprocess Crop for PP-OCRv4 (Resize to H=48, Normalize to [-1.0, 1.0], Transpose HWC -> NCHW)
        tensor = self._preprocess_for_onnx(plate_crop_bgr)

        # 2. Run ONNX Inference Session
        input_name = PlateOCREngine._session.get_inputs()[0].name
        outputs = PlateOCREngine._session.run(None, {input_name: tensor})
        preds = outputs[0][0]  # shape: [TimeSteps, 97]

        # 3. CTC Greedy Decoding
        raw_text, ocr_conf = self._ctc_greedy_decode(preds)

        # 4. Positional Normalization (State/District/Series/Number optical confusions)
        norm_result = self.normalizer.normalize(raw_text)
        candidate_plate = norm_result.normalized_plate

        # 5. Indian Plate Format Validation
        val_result = self.validator.validate(candidate_plate)

        # 6. Dynamic Compound Confidence
        validity_score = 1.0 if val_result.is_valid else 0.40
        final_conf = (
            0.45 * ocr_conf +
            0.25 * plate_quality +
            0.30 * validity_score -
            val_result.confidence_penalty
        )
        final_conf = round(max(0.0, min(1.0, final_conf)), 3)

        # 7. Readability State Categorization
        if final_conf >= 0.65 and val_result.is_valid:
            readability = "READABLE"
            final_plate = candidate_plate
        elif final_conf >= 0.40:
            readability = "LOW_CONFIDENCE"
            final_plate = candidate_plate
        else:
            readability = "UNREADABLE"
            final_plate = None

        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return PlateOCRResult(
            raw_text=raw_text,
            normalized_plate=final_plate,
            ocr_confidence=round(ocr_conf, 3),
            format_valid=val_result.is_valid,
            final_confidence=final_conf,
            readability=readability,
            components=val_result.components,
            ocr_engine=self.engine_name,
            engine_version=self.engine_version,
            ocr_latency_ms=latency_ms
        )

    def _preprocess_for_onnx(self, crop: np.ndarray) -> np.ndarray:
        """
        Preprocesses BGR image for PP-OCRv4 recognition input:
        1. Aspect-ratio preserving resize to standard height = 48
        2. Channel normalization: (x / 255.0 - 0.5) / 0.5
        3. Transpose HWC -> NCHW Float32 tensor
        """
        h, w = crop.shape[:2]
        target_h = 48
        target_w = max(48, int(w * (target_h / float(h))))
        resized = cv2.resize(crop, (target_w, target_h), interpolation=cv2.INTER_LINEAR)
        img_norm = (resized.astype(np.float32) / 255.0 - 0.5) / 0.5
        tensor = np.transpose(img_norm, (2, 0, 1))[np.newaxis, :, :, :].astype(np.float32)
        return tensor

    def _ctc_greedy_decode(self, preds: np.ndarray) -> Tuple[str, float]:
        """
        Performs CTC greedy argmax decoding over logits/softmax output tensor.
        Merges consecutive duplicates and collapses blank tokens (index 0).
        """
        pred_indices = np.argmax(preds, axis=1)
        pred_probs = np.max(preds, axis=1)

        char_list = PlateOCREngine._character_list
        text_chars = []
        char_probs = []
        prev_idx = 0

        for idx, prob in zip(pred_indices, pred_probs):
            if idx != 0 and idx != prev_idx:
                if idx < len(char_list):
                    text_chars.append(char_list[idx])
                    char_probs.append(float(prob))
            prev_idx = idx

        raw_text = "".join(text_chars).strip()
        avg_conf = float(np.mean(char_probs)) if char_probs else 0.0
        return raw_text, avg_conf
