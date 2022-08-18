x = 'Initial Allocation in Hours:'
y = 'Percentage of Allocation Used:'
z = 'Project Fair Share:'
f = open('orion_nems.log')
for line in f:
  if x in line:
      allocation = line[line.find(x)+len(x):]
  if y in line:
      used = line[line.find(y)+len(y):]
  if z in line:
      fair = line[line.find(z)+len(z):]

total = float(str.strip(allocation).replace(',', ''))
used  = total*float(str.strip(used).replace('%', ''))/100.
fairshare  = float(str.strip(fair))

print('allocated=',total)
print('used=',used)
print('fairshare=',fairshare)
