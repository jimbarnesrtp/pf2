import datetime

pf2Files = ["buildAdvGear2.py","buildAlchemicalItems.py", "buildSpellsv2.py", "buildWornItems.py", "buildWeapons.py", "buildWands.py", "buildTraits.py", "buildStructures.py", 
    "buildStaves.py", "buildSnares.py", "buildSkills.py", "buildShields.py", "buildServices.py", "buildRunes.py", "buildRituals.py", "buildMonsters.py", "buildMaterials.py",
    "buildHeldItems.py", "buildHazards.py", "buildDomains.py", "buildDeities.py", "buildConsumables.py", "buildConditions.py", "buildCompanions.py", "buildBackgrounds.py", 
    "buildArmor.py", "buildAncestryFeats.py", "buildFeats.py"]


dateString = datetime.date.today().strftime("%Y%m%d")
statusFile = "pf2Update-"+dateString+".txt"

from pathlib import Path

processedFiles = []

my_file = Path(statusFile)
print(statusFile)
if my_file.is_file():
    with open(statusFile, "r") as r:
        processedFiles = [line.rstrip() for line in r]
        print(processedFiles)

for fileName in pf2Files:
    if fileName not in processedFiles:
        try:
            print("Processing File:", fileName)
            exec(open(fileName).read())
            processedFiles.append(fileName)
        except Exception as e:
            print("Error processing file:", fileName, "Exception,", e)
    



f = open(statusFile, "w")
for name in processedFiles:
    f.write(name+"\n")
    
f.close
