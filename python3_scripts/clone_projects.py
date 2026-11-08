# Python 3
#  Clone all projects from a GitLab server
import os
import sys
import shutil
import getopt
import traceback
import datetime
import gitlab
import subprocess


############################################################################
# Command line arguments
############################################################################

class CliConfig:
    def __init__(self):
        self.scriptName = ""
        self.apiToken = ""
        self.server = ""
        self.actualRun = False
        self.outputDir = "backup"


def ShowHelp() -> None:
    """Print command-line usage and available options."""
    print(f"python {sys.argv[0]} [OPTIONS] OUTPUT_DIR")
    print("    -t TOKEN, --token=TOKEN             Set API token")
    print("    -s SERVER, --server=SERVER          Set server address")
    print("    -a, --actualRun                     Without this, the clone action will skip.")
    print("    -h, --help                          Show this help.")
    print(" ")
    print(
        f"Example: python {sys.argv[0]} -t 123456 -h git.host.com:8080 -u admin -a")


def GetArguments() -> CliConfig | None:
    """Parse command-line options and return the resulting configuration."""
    config = CliConfig()
    config.scriptName = sys.argv[0]

    try:
        opts, args = getopt.getopt(sys.argv[1:], "aht:s:", [
                                   "token=", "server=", "user="])
    except getopt.GetoptError:
        return None

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            ShowHelp()
            sys.exit(0)
        elif opt in ("-t", "--token"):
            config.apiToken = arg
        elif opt in ("-s", "--server"):
            config.server = arg
        elif opt in ("-a", "--actualRun"):
            config.actualRun = True
    if args and args[0] != '-':
        config.outputDir = args[0]

    # Check all variable set
    for key, value in vars(config).items():
        if isinstance(value, str) and value == "":
            print("!!%s not set" % key)
            ShowHelp()  
            return None

    return config

############################################################################
############################################################################


def main() -> None:
    """Application main."""
    cliConfig = GetArguments()
    if cliConfig is None:
        return

    # check output directory
    outputDir = os.path.abspath(cliConfig.outputDir)
    print(f"Output directory: {outputDir}")
    if not os.path.exists(outputDir):
        os.mkdir(outputDir)
        print(f"{outputDir} created.")
    elif (os.path.isfile(outputDir)):
        print(f"{outputDir} exists, but not a directory.")
        return

    #
    print(f"Authenticating with GitLab server: {cliConfig.server}")
    gl = gitlab.Gitlab(url=cliConfig.server, private_token=cliConfig.apiToken)
    gl.auth()

    #
    projectCount = 0
    pullCount = 0
    cloneCount = 0
    emptyCount = 0
    groups = gl.groups.list(get_all=True)
    for group in groups:
        print(f"Group: {group.name} (ID: {group.id})")
        groupDir = os.path.join(outputDir, group.name)
        if not os.path.exists(groupDir):
            os.makedirs(groupDir)
        print(f"  Group directory: {groupDir}")

        projects = group.projects.list(get_all=True)
        projectCount += len(projects)
        for project in projects:
            repoDir = os.path.join(groupDir, project.path)
            print(f"{"-" * 77}")
            print(f"    Project: {project.name} (ID: {project.id})")
            print(f"    Repository directory: {repoDir}")
            if not os.path.exists(repoDir):
                print(f"    Clone URL: {project.ssh_url_to_repo}")
                cmd = f"git clone {project.ssh_url_to_repo}"
                ret = subprocess.run(cmd, cwd=groupDir, shell=True)
                cloneCount += 1
            elif project.empty_repo:
                print(f"    Repository is empty.")
                emptyCount += 1
            else:
                print(f"    Pull URL: {project.ssh_url_to_repo}")
                cmd = f"git pull {project.ssh_url_to_repo}"
                ret = subprocess.run(cmd, cwd=repoDir, shell=True)
                pullCount += 1
            if ret.returncode != 0:
                print(f"    Command error: {ret.stderr.strip()}")
                return
            print(f"{"-" * 77}")

    # Summary
    timestampStr = datetime.datetime.now().isoformat()

    print("")
    print(f"{"=" * 77}")
    print(f"Timestamp: {timestampStr}")
    print(f"Output directory: {outputDir}")
    print(f"Total projects: {projectCount}")
    print(f"Total pulls: {pullCount}")
    print(f"Total clones: {cloneCount}")
    print(f"Total empty repositories: {emptyCount}")

    infoFile = os.path.join(outputDir, f"info.txt")
    if os.path.exists(infoFile):
        os.remove(infoFile)
    with open(infoFile, "w") as f:
        f.write(f"Timestamp: {timestampStr}\n")
        f.write(f"Output directory: {outputDir}\n")
        f.write(f"Total projects: {projectCount}\n")
        f.write(f"Total pulls: {pullCount}\n")
        f.write(f"Total clones: {cloneCount}\n")
        f.write(f"Total empty repositories: {emptyCount}\n")


    pass

############################################################################
############################################################################


if __name__ == '__main__':
    # Init
    try:
        main()
    except Exception as e:
        print("")
        print(f"ERROR: {e}")
        print(
            "============================================================================")
        print(traceback.format_exc())
        print(
            "============================================================================")
    finally:
        # DeInit
        pass
