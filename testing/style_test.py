import os
from src.transonic.modules.style import colors, banners, symbols, in_color, emph1, emph2, warn

def main():
    testing_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(testing_dir)
    style_path = os.path.join(base_dir, "src/transonic/modules/style.py")
       
     
    for k,v in banners.items():
        print(f"THEME: {k}")
        color = v[0]
        title = v[1]
        print(f"{in_color(color,title)}\n")
        print(f"\n{symbols.get("spade")*100}")

    print(f"{emph1("This is emphasis option 1")}")
    print(f"{emph2("This is emphasis option 2")}")
    print(f"{warn("this")} is a warning!")


        
    return 0
if __name__ == '__main__':
    status_code = main()

