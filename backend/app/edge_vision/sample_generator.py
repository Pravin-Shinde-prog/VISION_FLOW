import cv2
import numpy as np
from typing import List, Dict
from app.edge_vision.schemas import SampleFrameInfo


class SampleFrameGenerator:
    """
    Generates synthetic development vehicle and license plate frames
    covering multiple test scenarios (Clean HSRP, Night Glare, Rain Blur, Damaged Plate, Occluded Plate).
    Allows instant interactive testing and demonstration in the Edge Vision workbench.
    """

    @staticmethod
    def get_sample_catalog() -> List[SampleFrameInfo]:
        return [
            SampleFrameInfo(
                sample_id="clean_hsrp_day",
                title="Standard HSRP Plate (Daytime)",
                description="Clean Indian high-security registration plate on a white SUV in optimal lighting.",
                category="Standard",
                filename="clean_hsrp_day.jpg"
            ),
            SampleFrameInfo(
                sample_id="night_glare",
                title="Night Corridor with Headlight Glare",
                description="Night scene with strong specular reflection and high-contrast glare over front bumper.",
                category="Adverse Lighting",
                filename="night_glare.jpg"
            ),
            SampleFrameInfo(
                sample_id="rain_motion_blur",
                title="Monsoon Rain & Motion Blur",
                description="Degraded frame with motion blur and low illumination uniformity during heavy rain.",
                category="Adverse Weather",
                filename="rain_motion_blur.jpg"
            ),
            SampleFrameInfo(
                sample_id="damaged_cracked_plate",
                title="Physically Damaged / Bent Plate",
                description="Plate with structural fracture across border and localized paint loss.",
                category="Compliance Anomaly",
                filename="damaged_cracked_plate.jpg"
            ),
            SampleFrameInfo(
                sample_id="mud_occluded_plate",
                title="Mud / Dirt Occluded Plate",
                description="Severely dirty license plate with partial character occlusion from highway splash.",
                category="Occlusion",
                filename="mud_occluded_plate.jpg"
            ),
        ]

    @staticmethod
    def generate_sample_image(sample_id: str) -> np.ndarray:
        """
        Generates a synthetic BGR frame representing the specified test condition.
        """
        w, h = 960, 540
        img = np.zeros((h, w, 3), dtype=np.uint8)

        if sample_id == "night_glare":
            # Dark asphalt night background
            img[:] = (20, 22, 28)
            # Add vehicle hood & headlights
            cv2.rectangle(img, (220, 160), (740, 480), (45, 48, 55), -1)
            # Headlight glare halos
            cv2.circle(img, (280, 240), 90, (220, 240, 255), -1)
            cv2.circle(img, (680, 240), 90, (220, 240, 255), -1)
            # Plate area with glare washout
            px1, py1, px2, py2 = 380, 360, 580, 415
            cv2.rectangle(img, (px1, py1), (px2, py2), (240, 245, 250), -1)
            cv2.putText(img, "MH 12 DX 7741", (px1 + 15, py1 + 38), cv2.FONT_HERSHEY_DUPLEX, 0.75, (20, 20, 20), 2)
            # Strong specular highlight over plate center
            cv2.ellipse(img, (480, 385), (55, 20), 0, 0, 360, (255, 255, 255), -1)

        elif sample_id == "rain_motion_blur":
            # Rainy grey daylight background
            img[:] = (85, 90, 95)
            # Vehicle shape
            cv2.rectangle(img, (220, 150), (740, 470), (70, 75, 80), -1)
            # Bumper
            cv2.rectangle(img, (240, 340), (720, 450), (40, 42, 45), -1)
            # Plate with blur
            px1, py1, px2, py2 = 380, 365, 580, 415
            cv2.rectangle(img, (px1, py1), (px2, py2), (210, 215, 220), -1)
            cv2.putText(img, "MH 12 ER 3390", (px1 + 15, py1 + 36), cv2.FONT_HERSHEY_DUPLEX, 0.75, (30, 30, 30), 2)
            # Apply motion blur kernel
            k = np.zeros((15, 15))
            k[7, :] = 1.0 / 15.0
            img = cv2.filter2D(img, -1, k)
            # Add synthetic rain streaks
            for _ in range(80):
                rx = np.random.randint(0, w)
                ry = np.random.randint(0, h - 30)
                cv2.line(img, (rx, ry), (rx + 4, ry + 25), (190, 200, 210), 1)

        elif sample_id == "damaged_cracked_plate":
            # Daytime background
            img[:] = (140, 145, 150)
            cv2.rectangle(img, (200, 140), (760, 470), (30, 60, 140), -1) # Blue vehicle
            cv2.rectangle(img, (230, 320), (730, 450), (25, 25, 25), -1)
            # Plate with cracks & bent corner
            px1, py1, px2, py2 = 370, 355, 590, 415
            cv2.rectangle(img, (px1, py1), (px2, py2), (235, 235, 240), -1)
            cv2.putText(img, "MH 12 TC 9812", (px1 + 15, py1 + 42), cv2.FONT_HERSHEY_DUPLEX, 0.78, (15, 15, 15), 2)
            # Structural fracture line & hole
            cv2.line(img, (px1 + 80, py1), (px1 + 130, py2), (10, 10, 10), 3)
            cv2.circle(img, (px1 + 160, py1 + 18), 12, (25, 25, 25), -1) # Damage hole
            # Bent chipped corner
            pts = np.array([[px2 - 30, py1], [px2, py1], [px2, py1 + 25]], np.int32)
            cv2.fillPoly(img, [pts], (25, 25, 25))

        elif sample_id == "mud_occluded_plate":
            # Daylight road
            img[:] = (120, 125, 130)
            cv2.rectangle(img, (200, 140), (760, 470), (180, 185, 190), -1) # Silver vehicle
            cv2.rectangle(img, (230, 320), (730, 450), (35, 35, 35), -1)
            # Plate with mud patches
            px1, py1, px2, py2 = 370, 355, 590, 415
            cv2.rectangle(img, (px1, py1), (px2, py2), (220, 220, 220), -1)
            cv2.putText(img, "MH 12 KQ 5504", (px1 + 15, py1 + 42), cv2.FONT_HERSHEY_DUPLEX, 0.78, (20, 20, 20), 2)
            # Mud splashes across characters
            cv2.ellipse(img, (px1 + 90, py1 + 35), (40, 18), 15, 0, 360, (45, 60, 85), -1) # Mud brown/black
            cv2.ellipse(img, (px1 + 160, py1 + 25), (35, 22), -20, 0, 360, (40, 55, 75), -1)

        else:
            # Clean HSRP Standard Daytime
            img[:] = (160, 165, 170)
            # White SUV
            cv2.rectangle(img, (200, 130), (760, 470), (240, 242, 245), -1)
            cv2.rectangle(img, (230, 310), (730, 445), (30, 32, 35), -1) # Grille/Bumper
            # Clean HSRP plate
            px1, py1, px2, py2 = 370, 355, 590, 415
            cv2.rectangle(img, (px1, py1), (px2, py2), (250, 252, 255), -1)
            cv2.rectangle(img, (px1, py1), (px2, py2), (10, 10, 10), 2) # Border
            # Blue IND badge
            cv2.rectangle(img, (px1 + 4, py1 + 4), (px1 + 22, py2 - 4), (160, 60, 20), -1)
            cv2.putText(img, "IND", (px1 + 5, py1 + 22), cv2.FONT_HERSHEY_SIMPLEX, 0.28, (255, 255, 255), 1)
            cv2.putText(img, "MH 12 AB 1234", (px1 + 30, py1 + 42), cv2.FONT_HERSHEY_DUPLEX, 0.78, (10, 10, 10), 2)

        return img
