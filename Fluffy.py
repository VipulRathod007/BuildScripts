import os
import json
from Util import clean
from Configurations import *


def main(inMDEFPath: str, inOutputDir: str):
    if os.path.exists(inMDEFPath):
        inMDEFPath = os.path.abspath(inMDEFPath)
    else:
        print(f'Invalid MDEF path: {inMDEFPath}')

    configDir = os.path.join(inOutputDir, 'Configs')
    tablesDir = os.path.join(inOutputDir, 'Tables')
    skeletonTablesDir = os.path.join(inOutputDir, 'SkeletonTables')

    clean(configDir)
    clean(tablesDir)
    clean(skeletonTablesDir)

    with open(inMDEFPath, 'r') as file:
        mdefContent = json.load(file)
    mdef = MDEF(mdefContent)

    ConfigurationH.Configure(mdef, configDir)
    ConfigurationCPP.Configure(mdef, configDir)
    ConfigurationHelpersH.Configure(mdef, configDir)
    DriverWideConfigurationCPP.Configure(mdef, configDir)

    TableConfig.Configure(mdef, tablesDir)
    SkeletonTableConfig.Configure(mdef, skeletonTablesDir)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(f'Too few inputs\nRun python {os.path.basename(__file__)} <MDEFPath> <OutputDir>')
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
