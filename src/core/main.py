import sys
import time
from src.core.coach import PronunciationCoach
from src.utils import config

def print_welcome():
    print("\n" + "="*60)
    print("🎓 ECHOLINGUA - AI PRONUNCIATION COACH")
    print("="*60)
    print("\nWelcome! Select your practice level to begin.\n")

def select_category():
    print("📚 SELECT YOUR PRACTICE LEVEL:")
    print("="*60)
    print("1. 🟢 Basic")
    print("2. 🟡 Intermediate")
    print("3. 🔴 Advanced")
    print("4. 🎲 Random")
    print("="*60)
    
    while True:
        try:
            choice = input("\nEnter your choice (1-4): ").strip()
            
            if choice == "1":
                return "basic"
            elif choice == "2":
                return "intermediate"
            elif choice == "3":
                return "advanced"
            elif choice == "4":
                return "random"
            else:
                print("❌ Invalid choice. Please enter a number between 1 and 4.")
        
        except (EOFError, KeyboardInterrupt):
            print("\n\n👋 Goodbye!")
            sys.exit(0)

def main():
    print_welcome()
    
    try:
        config.validate_config()
    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        print("\nPlease:")
        print("1. Copy .env.example to .env")
        print("2. Add your API keys to the .env file")
        print("3. Run the application again")
        sys.exit(1)
    
    category = select_category()
    
    print(f"\n✅ Starting {category} level practice\n")
    
    input("Press Enter to begin... ")
    
    coach = PronunciationCoach(category=category)
    
    try:
        coach.run_iterative_practice()
        
        print("\n" + "="*60)
        coach.print_session_summary()
        print("="*60)
    
    except KeyboardInterrupt:
        print("\n\n⏸️  Application interrupted by user")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    finally:
        coach.cleanup()
        print("\n👋 Session ended")

if __name__ == "__main__":
    main()