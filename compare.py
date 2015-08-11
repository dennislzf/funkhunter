import os
import sys
import json
def compare_json(old_file,new_file):
    with open(old_file) as data_file:
        old_file_data = json.load(data_file)
    with open(new_file) as data_file:
        new_file_data = json.load(data_file)
    #get all that new data
    new_cnames =[]
    removed_cnames= []
    changed_cnames = []
    for new_json_data in new_file_data.get('cnames',None):
        new_json_data = json.loads(new_json_data)
        #if cname isnt found we know its new
        cname_found = False
        for index,old_json_data in enumerate(old_file_data.get('cnames',None)):
            old_json_data = json.loads(old_json_data)
            if new_json_data.get('cnameRecord') == old_json_data.get('cnameRecord'):
                cname_found = True
                if new_json_data.get('cname') != old_json_data.get('cname'):
                    changed_cnames.append(new_json_data)
                    # remove the cname so we don't need to iterate through it
                del old_file_data.get('cnames')[index]
        if cname_found == False:
            new_cnames.append(new_json_data)
    #all the cnames that remain are have not been removed.
    removed_cnames = old_file_data.get('cnames')
    cname_data= {}
    cname_data['new_cnames'] = new_cnames
    cname_data['removed_cnames'] = removed_cnames
    cname_data['changed_cnames'] = changed_cnames
    filename = "diffs/%s-vs-%s.json" % (old_file.split('/')[0], new_file.split('/')[1])
    with open(os.path.join('diffs', '%s-vs-%s.json' % (old_file.split('/')[1].split('.json')[0], new_file.split('/')[1].split('.json')[0])), 'w') as out:
        out.write(json.dumps(cname_data, sort_keys=True, indent=4, separators=(',', ': ')))










if __name__ == "__main__":
    if len(sys.argv) == 3:
        compare_json(sys.argv[1], sys.argv[2])
    else:
        print 'Usage: cname.py <plaintext file w/ URL on each line>'
