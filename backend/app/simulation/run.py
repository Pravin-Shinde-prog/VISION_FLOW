import argparse
import asyncio
from datetime import datetime, timezone
from app.simulation.config import SimulationConfig
from app.simulation.engine import TrafficSimulator


def parse_args():
    parser = argparse.ArgumentParser(description="VISION_FLOW Synthetic Traffic & Camera-Event Simulator")
    parser.add_argument("--vehicles", type=int, default=30, help="Number of synthetic vehicles (default: 30)")
    parser.add_argument("--events-per-vehicle", type=int, default=5, help="Sightings per vehicle (default: 5)")
    parser.add_argument("--seed", type=int, default=42, help="Deterministic random seed (default: 42)")
    return parser.parse_args()


async def main():
    args = parse_args()
    config = SimulationConfig(
        vehicle_count=args.vehicles,
        events_per_vehicle=args.events_per_vehicle,
        seed=args.seed,
    )

    print(f"[*] Starting VISION_FLOW Traffic Simulation with seed={config.seed}...")
    print(f"[*] Simulating {config.vehicle_count} vehicles, ~{config.events_per_vehicle} events each...")

    simulator = TrafficSimulator(config)
    result = await simulator.run()

    print("\n[+] Simulation Finished Successfully:")
    print(f"    - Vehicles Created: {result['vehicles_created']}")
    print(f"    - Plates Created:   {result['plates_created']}")
    print(f"    - Events Created:   {result['events_created']}")
    print(f"    - Execution Time:   {result['duration_seconds']}s")
    print(f"    - Time Span:        {result['start_time']} -> {result['end_time']}")


if __name__ == "__main__":
    asyncio.run(main())
