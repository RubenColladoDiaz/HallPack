import argparse
import re
import sys
import json
import pprint

def createArgs():
    parser = argparse.ArgumentParser()
    # Mirar si hago resolve-branch o next-version
    menu = parser.add_subparsers(dest="action", required=True ,help="Comandos disponibles")

    resolve_branch = menu.add_parser("resolve-branch", help="Devuelve la rama esperada del motor especificado")
    resolve_branch.add_argument("--branches", required=True, help="Especifica la ruta donde se encuentra el listado de ramas")
    # Porque puede ser mas de un tag
    resolve_branch.add_argument("tags", nargs="+", help="Listado de motores los cuales se quiere saber su rama")

    next_version = menu.add_parser("next-version", help="Devuelve la siguiente versión despues de cerrar la actual")
    next_version.add_argument("command_version", help="Version que se desea cerrar")
    next_version.add_argument("upload_type", choices=["patch", "minor", "major"], help="Tipo de subida de version")

    audit = menu.add_parser("audit", help="Devuelve si la herramienta esta lista para cerrar version o posibles errores")
    audit.add_argument("hubsync", help="Especifica la ruta donde se encuentra el estado de la rama de release justo antes de cerrar version")

    plan = menu.add_parser("plan", help="Devuelve el plan de actualizacion de una sala")
    plan.add_argument("--hall", required=True, help="Especifica la ruta donde se encuentra el estado actual de la sala")
    plan.add_argument("--target", required=True, help="Especifica la ruta donde se encuentra el estado deseado")
    plan.add_argument("--index", required=True, help="Especifica la ruta donde se encuentra el indice del repositorio de artefactos")


    return parser.parse_args()

def getBranches(args):
    with open(args.branches, encoding="utf-8") as f:
        branches = {line.strip() for line in f if line.strip()}
        return branches

def splitTag(tag):
    clear_tag = re.sub(r"_RC\d+$", "", tag, flags=re.IGNORECASE)
    return clear_tag.rsplit("_", 1)

def resolveRelease(version_numbers, name):
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
        if len(splitTag) != 2:
            print(f"ERROR: formato de tag inválido: {tag}", file=sys.stderr)
            sys.exit(1)
            
        name = splitted_tag[0]
        version = splitted_tag[1]
            
        version_numbers = version.split(".")
            
        while (len(version_numbers) > 1):
            version_numbers = version_numbers[:-1]
            text_release = resolveRelease(version_numbers, name)
                
            if text_release + "_stable" in branches:
                print(text_release + "_stable")
                break
            if text_release in branches:
                print(text_release)
                break
        else:
            print("ERROR para " + tag, file=sys.stderr)
            sys.exit(1)

def validateFormat(version_split):
    if len(version_split) != 3:
        print("No son 3 campos")
        sys.exit(1)

    for part in version_split:
        if len(part) != 2 or not part.isdigit():
            print("alguno de los campos no son 2 digitos", file=sys.stderr)
            sys.exit(1)

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

def limitVersion(v1, v2, v3):
    if v1 > 99 or v2 > 99 or v3 > 99:
        print("No se permite que se pase de 99", file=sys.stderr)
        sys.exit(1)

def updateVersion(args):
    version = args.command_version
    upload_type = args.upload_type
            
    version_split = version.split(".")
    validateFormat(version_split)
            
    v1 = int(version_split[0])
    v2 = int(version_split[1])
    v3 = int(version_split[2])
    
    new_version = calculateNextVersion(v1, v2, v3, upload_type)
    limitVersion(new_version[0], new_version[1], new_version[2])
        
    print(f"{new_version[0]:02d}.{new_version[1]:02d}.{new_version[2]:02d}")
    
def searchBuild(args):
    build = args.hubsync + "/build.sh"
    with open(build, encoding="utf-8") as f:
        for line in f:
            if line.startswith("TOOL_VERSION="):
                tool_split = line.split("=", 1)
                build_version = tool_split[1].strip().strip('"')
                break
    
    if build_version is None:
        print("ERROR: no se encontró TOOL_VERSION en build.sh", file=sys.stderr)
        sys.exit(1)
            
    return build_version

def searchChangelog(args):
    changelog = args.hubsync + "/CHANGELOG.ver"
    with open(changelog, encoding="utf-8") as f:
        for line in f:
            if "Version:" in line:
                version_split = line.split(":")
                changelog_version = version_split[1].strip()
                break
    
    if changelog_version is None:
        print("ERROR: no se encontró la versión en CHANGELOG.ver", file=sys.stderr)
        sys.exit(1)
    
    return changelog_version

def searchPyProjectToml(args):
    toml = args.hubsync + "/pyproject.toml"
    with open(toml, encoding="utf-8") as f:
        for line in f:
            if line.startswith("version"):
                line = line.replace('"', '')
                version_split = line.split("=")
                toml_version = version_split[1].strip()
                break

    if toml_version is None:
        print("ERROR: no se encontró la versión en pyproject.toml", file=sys.stderr)
        sys.exit(1)

    return toml_version

def searchVersionsTxt(args):
    versions_txt = args.hubsync + "/versions.txt"
    versions = []
    with open(versions_txt, encoding="utf-8") as f:
        for line in f:
            version = line.split("\n")[0]
            if version != "":
                versions.append(version)

    if versions == []:
        print("ERROR: no se encontró ninguna version en versions.txt", file=sys.stderr)
        sys.exit(1)

    return versions

def checkName(args, errors):
    toml = args.hubsync + "/pyproject.toml"
    build = args.hubsync + "/build.sh"
    toml_name = ""
    build_name = ""
    with open(toml, encoding="utf-8") as f:
        for line in f:
            if "name" in line:
                line_split = line.split("=")
                toml_name = line_split[1].replace('"', '').strip()
                break
    with open(build, encoding="utf-8") as f:
        for line in f:
            if line.startswith("TOOL_NAME="):
                line_split = line.split("=", 1)
                build_name = line_split[1].replace('"', '').strip()
                break

    if toml_name != build_name:
        errors.append(f"ERROR: Los nombres no concuerdan")

def checkDates(args, errors):
    changelog = args.hubsync + "/CHANGELOG.ver"
    dates = []
    rows_with_sharp = 0
    with open(changelog, encoding="utf-8") as f:
        for line in f:
            if "##" in line:
                rows_with_sharp += 1
            if rows_with_sharp >= 3:
                break
            if "Date:" in line:
                dates.append(line.split(":")[1].strip())
    dates.pop(0)

    for i in range(1, len(dates)):
        if dates[i] > dates[i - 1]:
            errors.append(f"ERROR: Fechas desordenadas en el CHANGELOG")
            break

def checkLogs(args, errors):
    git_log = args.hubsync + "/git_log.txt"
    changelog = args.hubsync + "/CHANGELOG.ver"
    logs = []
    clogs= []
    with open(git_log, encoding="utf-8") as f:
        for line in f:
            logs.append(line.split(" ", 1)[1].replace("\n", ""))
            
    with open(changelog, encoding="utf-8") as f:
        for line in f:
            if "-" in line:
                clogs.append(line.split("-", 1)[1].replace("\n", "").replace(" ", "", 1))
        clogs.pop()
    
    for clog in clogs:
        if clog not in logs:
            errors.append("ERROR: Los logs de git_log y CHANGELOG no coinciden")
            break

def checkVersions(args, errors):
    build_version = searchBuild(args)
    changelog_version = searchChangelog(args)
    toml_version = searchPyProjectToml(args)
    available_versions = searchVersionsTxt(args)

    if build_version not in available_versions or changelog_version not in available_versions or toml_version not in available_versions:
        errors.append(f"ERROR: La version no se encuentra en versions.txt")

    if build_version != changelog_version or build_version != toml_version:
        errors.append(f"ERROR: Los archivos contienen versiones distintas")

def makeAudit(args):
    errors = []

    checkVersions(args, errors)
    checkName(args, errors)
    checkDates(args, errors)
    checkLogs(args, errors)
    
    if len(errors) > 0:
        for error in errors:
            print(error, file=sys.stderr)
        sys.exit(1)
    else:
        print("OK")

def checkEnginesVersions(hall_state, target, notes):
    hall_engine = None
    target_engine = None
    for mix in hall_state["mixes"]:
        hall_engine = mix["engine"]
        engine_split = hall_engine.split("_", 1)
        for tmix in target["mixes"]:
            target_engine = tmix["engine"]
            tengine_split = target_engine.split("_", 1)
            if(engine_split[0] == tengine_split[0]):
                if engine_split[1] != tengine_split[1]:
                    notes.append(f"La version de motor ha cambiado. Target: {target_engine}. Hall: {hall_engine}.")
                    break

def checkGames(hall_state, target, notes):
    for mix in hall_state["mixes"]:
        for game in mix["games"]:
            found = False
            for tmix in target["mixes"]:
                for tgame in tmix["games"]:
                    if(game["acronym"] == tgame["acronym"]):
                        found = True
                        if(game["version"] != tgame["version"]):
                            notes.append(f"La version del juego {game["acronym"]} ha cambiado. {game["version"]} -> {tgame["version"]}.")
                            break
            if not found:
                notes.append(f"El juego {game['acronym']} está en la sala pero no en el target.")
                
    for tmix in target["mixes"]:
        for tgame in tmix["games"]:
            found = False
            for mix in hall_state["mixes"]:
                for game in mix["games"]:
                    if tgame["acronym"] == game["acronym"]:
                        found = True
            if not found:
                notes.append(f"El juego {tgame['acronym']} está en el target pero no en la sala.")
                
def browseArtefactsIndex(args):
    browse_folder = args.index

def makePlan(args):
    notes = []

    hall_state = None
    target = None
    with open(args.hall, 'r') as f:
        hall_state = json.load(f)
    with open(args.target, 'r') as f:
        target = json.load(f)
    
    checkEnginesVersions(hall_state, target, notes)
    checkGames(hall_state, target, notes)
    browseArtefactsIndex(args)

    for note in notes:
        print(note)

def main():
    args = createArgs()

    match args.action:
        case "resolve-branch":
            resolveBranch(args)
        case "next-version":
            updateVersion(args)
        case "audit":
            makeAudit(args)
        case "plan":
            makePlan(args)

if __name__ == "__main__":
    main()