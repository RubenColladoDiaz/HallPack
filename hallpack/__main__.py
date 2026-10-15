import argparse
import re
import sys

def createArgs():
    parser = argparse.ArgumentParser()
    # Mirar si hago resolve-branch o next-version
    menu = parser.add_subparsers(dest="action", help="Comandos disponibles")

    resolve_branch = menu.add_parser("resolve-branch", help="Devuelve la rama esperada del motor especificado")
    resolve_branch.add_argument("--branches", required=True, help="Especifica la ruta donde se encuentra el listado de ramas")
    # Porque puede ser mas de un tag
    resolve_branch.add_argument("tags", nargs="+", help="Listado de motores los cuales se quiere saber su rama")

    next_version = menu.add_parser("next-version", help="Devuelve la siguiente versión despues de cerrar la actual")
    next_version.add_argument("command_version", help="Version que se desea cerrar")
    next_version.add_argument("upload_type", choices=["patch", "minor", "major"], help="Tipo de subida de version")

    audit = menu.add_parser("audit", help="Devuelve si la herramienta esta lista para cerrar version o posibles errores")
    audit.add_argument("hubsync", help="Especifica la ruta donde se encuentra el estado de la rama de release justo antes de cerrar version")

    return parser.parse_args()

def getBranches(args):
    with open(args.branches, encoding="utf-8") as f:
        branches = {line.strip() for line in f if line.strip()}
        return branches

def splitTag(tag):
    clear_tag = re.sub(r"_RC\d+$", "", tag, flags=re.IGNORECASE)
    return clear_tag.rsplit("_", 1)

def resolveRelease(version_numbers, name):
    version_numbers = version_numbers[:-1]
    text_version = ""
    for version_number in version_numbers:
        text_version += version_number + "."
    
    text_version = text_version.rstrip(".")
    text_version += ".X"
                
    return "releases/" + name + "_" + text_version

def resolveBranch(args):
    branches = getBranches(args)
        
    for tag in args.tags:
        splitted_tag = splitTag(tag)
        name = splitted_tag[0]
        version = splitted_tag[1]
            
        version_numbers = version.split(".")
            
        while (len(version_numbers) > 1):              
            text_release = resolveRelease(version_numbers, name)
                
            if text_release + "_stable" in branches:
                print(text_release + "_stable")
                break
            if text_release in branches:
                print(text_release)
                break
        else:
            print("ERROR para " + tag)
            sys.exit(1)

def validateFormat(version_split):
    if len(version_split) != 3:
        print("No son 3 campos")
        sys.exit(1)
        return

    for part in version_split:
        if len(part) != 2 or not part.isdigit():
            print("alguno de los campos no son 2 digitos")
            sys.exit(1)
            return

def calculateNextVersion(v1, v2, v3, upload_type):
    match upload_type:
        case "patch":
            v3 += 1
        case "minor":
            v2 += 1
            v3 = 0
        case "major":
            v1 += 1
            v2 = 0
            v3 = 0
    
    return [v1, v2, v3]

def limitVersion(new_version):
    if new_version.v1 > 99 or new_version.v2 > 99 or new_version.v3 > 99:
        print("No se permite que se pase de 99")
        sys.exit(1)
        return

def updateVersion(args):
    version = args.command_version
    upload_type = args.upload_type
            
    version_split = version.split(".")
    validateFormat(version_split)
            
    v1 = int(version_split[0])
    v2 = int(version_split[1])
    v3 = int(version_split[2])
    
    new_version = calculateNextVersion(v1, v2, v3, upload_type)
    limitVersion(new_version)
        
    print(f"{new_version.v1:02d}.{new_version.v2:02d}.{new_version.v3:02d}")
    
def searchBuild(args):
    build = args.hubsync + "/build.sh"
    with open(build, encoding="utf-8") as f:
        for line in f:
            if line.startswith("TOOL_VERSION="):
                tool_split = line.split("=")
                build_version = tool_split[1].strip().strip('"')
                break
            
    return build_version

def searchChangelog(args):
    changelog = args.hubsync + "/CHANGELOG.ver"
    with open(changelog, encoding="utf-8") as f:
        for line in f:
            if "Version:" in line:
                version_split = line.split(":")
                changelog_version = version_split[1].strip()
                break
    
    return changelog_version

def makeAudit(args):
    errors = []
    
    build_version = searchBuild(args)
    changelog_version = searchChangelog(args)
                
    if build_version != changelog_version:
        errors.append(f"ERROR: build.sh tiene {build_version} pero CHANGELOG.ver tiene {changelog_version}")
        
    if len(errors) > 0:
        for error in errors:
            print(error)
        sys.exit(1)
    else:
        print("OK")

def main():
    args = createArgs()
    
    if args.action == "resolve-branch":
        resolveBranch(args)
        
    elif args.action == "next-version":
        updateVersion(args)
    
    elif args.action == "audit":
        makeAudit(args)
                    
if __name__ == "__main__":
    main()