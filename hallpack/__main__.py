import argparse
import re

parser = argparse.ArgumentParser()
menu = parser.add_subparsers(dest="action") # Mirar si hago resolve-branch o next-version

resolve_branch = menu.add_parser("resolve-branch")
resolve_branch.add_argument("--branches", required=True)
resolve_branch.add_argument("tags", nargs="+") # Porque pueed ser mas de un tag

next_version = menu.add_parser("next-version")
next_version.add_argument("command_version")
next_version.add_argument("upload_type", choices=["patch", "minor", "major"])

args = parser.parse_args()

def clearTag(tag):
    return re.sub(r"_RC\d+$", "", tag, flags=re.IGNORECASE)

def findRemote():
    if args.action == "resolve-branch":
        
        with open(args.branches, encoding="utf-8") as f:
               branches = {line.strip() for line in f if line.strip()}
        
        for tag in args.tags:
            clear_tag = clearTag(tag)
            splitted_tag = clear_tag.rsplit("_", 1)
            name = splitted_tag[0]
            version = splitted_tag[1]
            version_numbers = version.split(".")
            
            while (len(version_numbers) > 1):
                version_numbers = version_numbers[:-1]
                text_version = ""
                for version_number in version_numbers:
                    text_version += version_number + "."
                text_version = text_version.rstrip(".")
                text_version += ".X"
                
                text_release = "releases/" + name + "_" + text_version
                
                if text_release + "_stable" in branches:
                    print(text_release + "_stable")
                    break
                if text_release in branches:
                    print(text_release)
                    break
            else:
                print("ERROR para " + tag)
        
    elif args.action == "next-version":
        version = args.command_version
        upload_type = args.upload_type
            
        version_split = version.split(".")
        print(version_split)
        v1 = int(version_split[0])
        v2 = int(version_split[1])
        v3 = int(version_split[2])
            
findRemote()