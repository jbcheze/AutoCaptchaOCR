# ================================================================================================================================
# APPLICATION 
# ================================================================================================================================

from captcha_solver import CaptchaSolver

def demonstration_model(image_path):
    print(f"Processing {image_path}")
    solution = "abcde"
    return solution

def main():
    solver = CaptchaSolver()
    result = solver.solve_with_model(
        url="https://rutracker.org/forum/profile.php?mode=register",
        model_callback=demonstration_model, 
        human_like=True 
    )
    
    # Final results
    print(f"URL : {result['url']}")
    print(f"Solution : {result['solution']}")
    print(f"Success : {result['success']}")

    if result['success']:
        print("CAPTCHA was solved!")
    elif result['success'] is False:
        print("CAPTCHA was NOT solved. Wrong solution.")
    else:
        print("Uncertain. Could not verify.")
    
    # Browser is opened to keep the same CAPTCHA
    input("Press enter to close browser")
    solver.close()
    print("Browser closed")

if __name__ == "__main__":
    main()
