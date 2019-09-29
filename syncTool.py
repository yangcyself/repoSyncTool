import git
import time
import os
from datetime import datetime
import json
import glob

def get_modified_time(g,filename):
    try:
        changedtime = g.log('-1','--format="%ai"',filename)
    except git.exc.GitCommandError:
        print("no such file")
        return None
    if(not changedtime): return None
    changedtime = changedtime[1:-7]
    # print("time: ",changedtime)
    datetime_object = datetime.strptime(changedtime, '%Y-%m-%d %H:%M:%S')
    return datetime_object


def force_copy_file(gs,gd,file_source,file_target):
    source_path = os.path.join(gs.working_dir,file_source)
    target_path = os.path.join(gd.working_dir,file_target)
    os.system('cp -f "{}" "{}"'.format(source_path,target_path))


def sync_two_files(g1,g2,file1,file2):
    modifiedtime1 = get_modified_time(g1,file1)
    modifiedtime2 = get_modified_time(g2,file2)
    if(not modifiedtime1):
        force_copy_file(g2,g1,file2,file1)
    elif(not modifiedtime2 or (modifiedtime1 - modifiedtime2).total_seconds()>10):
        # file1 is newer
        force_copy_file(g1,g2,file1,file2)
    elif((modifiedtime1 - modifiedtime2).total_seconds()<-10):
        force_copy_file(g2,g1,file2,file1)
    

def add_commit_push(g):
    g.add(".")
    try:
        g.commit('-m "auto_sync at {}"'.format(datetime.today().strftime("%c")))
    except:
        pass
    g.push()

def sync_one_pair(g1,g2,name1,name2):
    """
    this method calls on sync_two_files, it handles parses the directories, 
        if two names are about directories, then all files in them are synced
    """
    # judge whether is directories
    name1 = os.path.join(g1.working_dir,name1)
    name2 = os.path.join(g2.working_dir,name2)
    # print("pair:",name1,name2)
    # if the conterpart is not in the directory, just force copy
    if(not os.path.exists(name1)):
        # print(name1,"NOT EXIST")
        os.system('cp -f -r "{}" "{}"'.format(name2,name1))
        return
    elif(not os.path.exists(name2)):
        # print(name2,"NOT EXIST")
        os.system('cp -f -r "{}" "{}"'.format(name1,name2))
        return

    if(os.path.isfile(name1)):
        # assert(os.path.isfile(name2))
        sync_two_files(g1,g2,name1,name2)
        # print("sync:",name1,name2)
        return
    
    # check all the files and subdirectories
    checks = set()
    # print(name1)
    r1,d1,f1 = next(os.walk(name1))
    for d in d1:
        checks.add((os.path.join(name1,d), os.path.join(name2,d)))
    for f in f1:
        checks.add((os.path.join(name1,f), os.path.join(name2,f)))
    # print(name2)
    r2,d2,f2 = next(os.walk(name2))
    for d in d2:
        checks.add((os.path.join(name1,d), os.path.join(name2,d)))
    for f in f2:
        checks.add((os.path.join(name1,f), os.path.join(name2,f)))

    for c1,c2 in checks:
        sync_one_pair(g1,g2,c1,c2)

def sync_two_repo(jsondict):
    repo_path1 = jsondict["repo1_path"]
    repo_path2 = jsondict["repo2_path"]
    g1 = git.cmd.Git(repo_path1)
    g2 = git.cmd.Git(repo_path2)
    g1.pull()
    g2.pull()
    sync_pairs = jsondict["sync_pairs"]
    for p in sync_pairs:
        filename1 = p["file_name1"]
        filename2 = p["file_name2"]
        sync_one_pair(g1,g2,filename1,filename2)
    add_commit_push(g1)
    add_commit_push(g2)

with open("./synclist.json","r") as f:
    info = json.load(f)

# print(info)
sync_two_repo(info)
