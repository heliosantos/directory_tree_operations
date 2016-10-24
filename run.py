import xml.etree.ElementTree as ET
import msvcrt
import argparse

from filesystem_crawler import FilesystemCrawler
from filesystem_crawler import parse_match_rules


def main():
    args = parse_arguments()

    baseDirPath, rawPatterns, opsConfs = parse_config_file(args.conf_file_path)

    matchrules, errors = parse_match_rules(baseDirPath, rawPatterns)

    print("\n[Match Rules]")
    for rule in matchrules:
        print('{type} {polarity} {pattern}'.format(
              type='d' if rule.dirsOnly else 'f' if rule.filesOnly else ' ',
              polarity='+' if rule.polarity else '-',
              pattern=rule.pattern.pattern), end='')

        print('' if rule.contentPattern is None else
              " containing '%s'" % rule.contentPattern)

    if errors:
        print("\n[Match Errors]")
        for line, error in errors:
            print('Line {line}: {error}'.format(
                line=str(line), error=str(error)))

    operators = load_operators(opsConfs)

    print("\n[File Operation]")
    for operator in operators:
        print('{description}'.format(description=operator.description()))
    print("\nExecute (y/n)\n")

    while True:
        key = ord(msvcrt.getch())
        if key == ord('y'):
            break
        if key == ord('n'):
            return

    def match_callback(match):
        for operator in operators:
            operator.apply(match[0])

    crawler = FilesystemCrawler(matchrules, match_callback)
    matchedPaths = crawler.search(baseDirPath)

    print('\n{} matches'.format(len(matchedPaths)))

    print("\nAll done")
    msvcrt.getch()


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--conf_file_path',
                        nargs='?',
                        default='config.xml',
                        help='the configuration file location')
    args = parser.parse_args()
    return args


def parse_config_file(configFilePath):
    root = ET.parse(configFilePath)
    baseDirPath = root.findtext('baseDirectoryPath').strip()
    rawMatchPatterns = root.findtext('matchPatterns')

    operators = []
    for op in root.find('operators').findall('operator'):
        opConf = {}
        opConf['name'] = op.attrib['name']
        opConf['module'] = op.attrib['module']
        opConf['shortcut'] = op.attrib['shortcut']
        params = {}
        for param in op.getchildren():
            params[param.tag] = param.text.strip()
        opConf['params'] = params
        operators.append(opConf)

    return baseDirPath, rawMatchPatterns, operators


def load_operators(operatorsConfigurations):
    operators = []
    for opConf in operatorsConfigurations:
        opClass = getattr(__import__(opConf['module']), opConf['name'])
        opInstance = opClass()

        for name, value in opConf['params'].items():
            opInstance.__dict__[name] = value
        operators.append(opInstance)

    return operators


if __name__ == '__main__':
    main()
