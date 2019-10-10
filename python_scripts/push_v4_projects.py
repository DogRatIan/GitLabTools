# Python 2.7
#  Push all projects to a GitLab server (V4 API)
import os
import sys
import shutil
import json
import urllib2, ssl
import getopt

gConfig = {"apiToken":"", "server":"", "httpUsername":"", "actualRun":False, "inputDir":"clone"}

############################################################################
# Command line arguments
############################################################################
def ShowHelp():
    print ("python %s [OPTIONS] INPUT_DIR" % sys.argv[0])
    print ("    -t TOKEN, --token=TOKEN             Set API token")
    print ("    -s SERVER, --server=SERVER          Set server address")
    print ("    -u USERNAME, --user=USERNAME        Set HTTPS username")
    print ("    -a, --actualRun                     Without this, the push action will skip.")
    print ("    -h, --help                          Show this help.")
    print (" ")
    print ("Example: python %s -t 123456 -h git.host.com:8080 -u admin -a" % sys.argv[0])

def GetArguments():
    try:
        opts, args = getopt.getopt(sys.argv[1:],"aht:s:u:p:",["actualRun","help","token=","server=","user=","password="])
    except getopt.GetoptError:
        ShowHelp ()
        sys.exit(1)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            ShowHelp ()
            sys.exit(0)
        elif opt in ("-t", "--token"):
            gConfig["apiToken"] = arg
            print ("apiToken=%s" % arg)
        elif opt in ("-s", "--server"):
            gConfig["server"] = arg
            print ("server=%s" % arg)
        elif opt in ("-u", "--user"):
            gConfig["httpUsername"] = arg
        elif opt in ("-a", "--actualRun"):
            gConfig["actualRun"] = True
    if args and args[0] != '-':
        gConfig["inputDir"] = args[0]
    # Check all variable set
    for key in gConfig.keys():
        if (gConfig[key] == ""):
            print ("!!%s not set" % key)
            ShowHelp ()
            sys.exit(1)

    return gConfig

############################################################################
############################################################################
def GetProjectListHeader(aItem):
    try:
        url = "https://" + gConfig["server"] + "/api/v4/projects"
        ctx = ssl._create_unverified_context()
        req = urllib2.Request(url)
        req.add_header ("PRIVATE-TOKEN", gConfig["apiToken"])
        response = urllib2.urlopen(req, context=ctx)
        return int (response.info ()[aItem])
    except urllib2.URLError as error:
        print ("GetProjectListHeader: %s" % error.reason)
    except ValueError:
        print("GetProjectListHeader: JSON parse error.")
    except:
        print("GetProjectListHeader: Unexpected error:", sys.exc_info()[0])
    return -1

############################################################################
############################################################################
def GetProjectPage(aPage):
    try:
        url = "https://" + gConfig["server"] + "/api/v4/projects" + "?page=" + str(aPage)
        print ("URL: %s" % url)
        ctx = ssl._create_unverified_context()
        req = urllib2.Request(url)
        req.add_header ("PRIVATE-TOKEN", gConfig["apiToken"])
        response = urllib2.urlopen(req, context=ctx)
        html = response.read()
        j_obj = json.loads(html)
        return j_obj
    except urllib2.URLError as error:
        print ("GetProjectPage: %s" % error.reason)
    except ValueError:
        print("GetProjectPage: JSON parse error.")
    except:
        print("GetProjectPage: Unexpected error:", sys.exc_info()[0])
    return None

############################################################################
############################################################################
def GetProjectList ():
    # Get number of pages
    num_of_pages = GetProjectListHeader("X-Total-Pages")
    if (num_of_pages < 0):
        return None
    print ("Number of pages=%d" % num_of_pages)

    # Get all page and append together
    j_ret = json.loads ("[]")
    for page in range (1, num_of_pages + 1):
        j_obj = GetProjectPage(page)
        if (j_obj is None):
            return None
        for x in j_obj:
            j_ret.append(x)

    return j_ret


############################################################################
############################################################################
def GetNamespaces():
    try:
        url = "https://" + gConfig["server"] + "/api/v4/namespaces"
        print ("URL: %s" % url)
        ctx = ssl._create_unverified_context()
        req = urllib2.Request(url)
        req.add_header ("PRIVATE-TOKEN", gConfig["apiToken"])
        response = urllib2.urlopen(req, context=ctx)
        html = response.read()
        j_obj = json.loads(html)
        return j_obj
    except urllib2.URLError as error:
        print ("GetNamespaces: URL error:%s " % error.reason)
    except ValueError:
        print("GetNamespaces: JSON parse error.")
    except:
        print("GetNamespaces: Unexpected error:", sys.exc_info()[0])
    return None

############################################################################
############################################################################
def ReadProjectList():
    try:
        list_file = gConfig["inputDir"] + "/list.json"
        with open(list_file, "r") as read_file:
            data = json.load(read_file)
            return data
    except IOError as e:
        print "ReadProjectList: I/O error({0}): {1}".format(e.errno, e.strerror)
    except:
        print("ReadProjectList: Unexpected error:", sys.exc_info()[0])
    return None

############################################################################
############################################################################
def CheckNamespaces (aList, aNamespace):
    for prj in aList:
        prj_name = prj["name"]
        prj_namespace = prj["namespace"]["name"]
        found = False
        for ns in aNamespace:
            if (ns["name"] == prj_namespace):
                found = True
                break
        if (not found):
            print ("Project '%s': Namespace '%s' not found." % (prj_name, prj_namespace))
            return False
    return True

############################################################################
############################################################################
def FindNamespaceId (aNsName, aNsList):
    for ns in aNsList:
        if (ns["name"] == aNsName):
            return int(ns["id"])
    return -1


############################################################################
############################################################################
def CreateProjesct (aName, aPath, aNsId, aDesc):
    try:
        print ("Creating '%s" % aName)
        url = "https://" + gConfig["server"] + "/api/v4/projects"
        url += "?name=" + urllib2.quote(aName)
        url += "&path=" + urllib2.quote(aPath)
        url += "&visibility=private"
        url += "&auto_devops_enabled=false"
        url += "&description=" + urllib2.quote(aDesc)
        url += "&namespace_id=" + str(aNsId)
        print ("URL: %s" % url)
        if (gConfig["actualRun"]):
            ctx = ssl._create_unverified_context()
            req = urllib2.Request(url)
            req.add_header ("PRIVATE-TOKEN", gConfig["apiToken"])
            response = urllib2.urlopen(req, context=ctx, data=" ")
            html = response.read()
            j_obj = json.loads(html)
#            print ("HTTP RESP: %s" % json.dumps (j_obj, indent=2))
        else:
            print ("HTTP skipped.")
        return True
    except urllib2.URLError as error:
        print ("Project '%s', URL error:%s " % (aName, error.reason))
    except ValueError:
        print("Project '%s', JSON parse error." % aName)
    except:
        print("Project '%s', Unexpected error:", (aName, sys.exc_info()[0]))
    return False

############################################################################
############################################################################
def FindProject (aName, aNamespace, aList):
    for x in aList:
        if (x["name"] == aName) and (x["namespace"]["name"] == aNamespace):
            return x
    return None

############################################################################
# Start
############################################################################
gConfig = GetArguments()

print ("Input directory: %s" % gConfig["inputDir"])

# Check input directory
if (not os.path.isdir (gConfig["inputDir"])):
    print("%s not found." % gConfig["inputDir"])
    sys.exit (1)
elif (os.path.isfile (gConfig["inputDir"])):
    print("%s is a file." % gConfig["inputDir"])
    sys.exit (1)

# Get namespaces from server
j_namespaces = GetNamespaces ()
if (j_namespaces is None):
    sys.exit (1)
#print (json.dumps (j_namespaces, indent=2))

# Load file project list
j_project_list = ReadProjectList()
if (j_project_list is None):
    sys.exit (1)
print ("%d projects loaded from file." % len ([prj for prj in j_project_list]))

# Check all namespace exist
if (CheckNamespaces (j_project_list, j_namespaces)):
    print ("All namespace found.")

# Get server projects
server_project_list = GetProjectList ()
if (server_project_list is None):
    sys.exit (1)

print ("%d projects found in server." % len ([prj for prj in server_project_list]))

# Creat projects
for prj in j_project_list:
    path = gConfig["inputDir"] + "/" + prj["path_with_namespace"] + ".git"
    git_url = "https://" + gConfig["httpUsername"] + ":" + gConfig["apiToken"] + "@" + gConfig["server"] + "/" + prj["path_with_namespace"] + ".git"

    # Check path
    if (not os.path.exists (path)):
        print ("'%s' not found" % path)
        sys.exit (1)

    # Remove Git origin
    cmd = "cd " + path
    cmd += " && git remote rm origin"
    print ("CMD: %s" % cmd)
    if (gConfig["actualRun"]):
        if (os.system (cmd)):
            print ("Command error!")
    else:
        print ("Command skipped.")

    # Add Git remote
    cmd = "cd " + path
    cmd += " && git remote add origin " + git_url
    print ("CMD: %s" % cmd)
    if (gConfig["actualRun"]):
        if (os.system (cmd)):
            print ("Command error!")
    else:
        print ("Command skipped.")

    #
    prj_name = prj["name"]
    prj_namespace = prj["namespace"]["name"]
    prj_desc = prj["description"]
    prj_path = prj["path"]

    #
    if (FindProject (prj_name, prj_namespace, server_project_list) is None):
        # Create project
        ns_id = FindNamespaceId (prj_namespace, j_namespaces)
        if (ns_id <= 0):
            print ("%s ID not found." % prj_namespace)
            sys.exit (1)
        if (not CreateProjesct (prj_name, prj_path, ns_id, prj_desc)):
            print ("HTTP create project fail.")
            sys.exit (1)
    else:
        print ("'%s' existed, skip creation." % prj_name)

    # Push to Git
    dir_count = len ([name for name in os.listdir(path)])
    if (dir_count > 1):
        cmd = "cd " + path
        cmd += " && env GIT_SSL_NO_VERIFY=true git push origin --all"
        print ("CMD: %s" % cmd)
        if (gConfig["actualRun"]):
            if (os.system (cmd)):
                print ("Command error!")
                sys.exit (1)
        else:
            print ("Command skipped.")

        cmd = "cd " + path
        cmd += " && env GIT_SSL_NO_VERIFY=true git push origin --tags"
        print ("CMD: %s" % cmd)
        if (gConfig["actualRun"]):
            if (os.system (cmd)):
                print ("Command error!")
                sys.exit (1)
        else:
            print ("Command skipped.")

#
print ("All Done.")