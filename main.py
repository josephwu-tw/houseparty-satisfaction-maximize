"""
House Party Optimizer - Entry Point

A dynamic programming solution for optimizing house party planning.

Authors: Chen-Yen Wu, Jinghong Yang, Yuting Wan
Version: 2.1.0
"""
import sys

def main():
    try:
        from app import PartyPlannerApp
        app = PartyPlannerApp()
        app.run()
    except KeyboardInterrupt:
        print("\n\nTerminated.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()