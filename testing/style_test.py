import os


from src.transonic.modules.style import colors, titles, symbols
def main():
    testing_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(testing_dir)
    style_path = os.path.join(base_dir, "src/transonic/modules/style.py")
       
     
    for k,v in titles.items():
        print(f"THEME: {k}\n{v}\nExample Text:  Lorem ipsum dolor sit amet...\n{colors.get("reset")}{symbols.get("spade")*100}")
        print(f"{colors.get("reset")}")
        
    return 0
if __name__ == '__main__':
    return_code = main()
    print(return_code)
