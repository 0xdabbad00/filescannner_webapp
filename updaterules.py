#!/usr/bin/python
# file: updaterules.py

import utils
import sys

if len(sys.argv) < 2:
	print "Usage: %s <rules_file>" % sys.argv[0]
	sys.exit(0)

rulesFile = sys.argv[1]
print "Loading rules from %s" % rulesFile

# Read the rules file
with open(rulesFile) as f:
	rulesData = f.read()

# Extract out each rule
rule = {'name': '', 'description': '', 'text': ''}
rules = []
for line in rulesData.split('\n'):
	if line.startswith('rule'):
		# Add previous rule to list
		if rule['text'] != '':
			rules.append(rule)
			rule = {'name': '', 'description': '', 'text': ''}
		rule['name'] = line.replace('rule', '').strip()
	if line.strip().startswith('description'):
		rule['description'] = line.replace('description =', '').replace('\"', '').strip()
	rule['text'] += line + '\n'
rules.append(rule)

cur, db = utils.connectToDB()

# Disable all previous rules
stmt = "UPDATE rules set enabled = 0"
cur.execute(stmt)
db.commit()

# Add our new rules
for rule in rules:
	stmt = "INSERT INTO rules (name, description) VALUES (%(name)s, %(description)s)"
	cur.execute(stmt, {'name': rule['name'], 'description': rule['description']})
	rule_id = cur.lastrowid
	db.commit()
	
	stmt = "INSERT INTO rules_text (id, text) VALUES (%(id)s, %(text)s)"
	cur.execute(stmt, {'id': rule_id, 'text': rule['text']})
	db.commit()

	print "Added rule %s" % rule['name']

db.close()
print "Complete"