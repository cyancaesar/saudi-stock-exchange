from src.config import setup_environment_and_logging
import argparse
import os

logger = setup_environment_and_logging()

def seed_db():
    from src.seed import seed
    seed()

def run_app():
    os.system("python -m streamlit run src/app.py")

def main():
    parser = argparse.ArgumentParser(description="Saudi Stock Exchage Data App CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    seed_parser = subparsers.add_parser("seed", help="Seed MongoDB database ")
    run_app_parser = subparsers.add_parser("app", help="Run Streamlit app")

    args = parser.parse_args()

    if args.command == "seed":
        seed_db()
    elif args.command == "app":
        run_app()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Exiting...")