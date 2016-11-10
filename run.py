import xmltodict
import msvcrt
import argparse

from filesystem_crawler import FilesystemCrawler
from filesystem_crawler import parse_match_rules


def main():
    args = parse_arguments()

    baseDirPath, rawPatterns, opsConfs, ignoreMatchedDirSubtree = (
        parse_config_file(args.conf_file_path))

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

    if not args.skipConfirmation:
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
    matchedPaths = crawler.search(baseDirPath, ignoreMatchedDirSubtree)

    print('\n{} matches'.format(len(matchedPaths)))


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--conf_file_path',
                        nargs='?',
                        default='config.xml',
                        help='the configuration file location')

    parser.add_argument('--skipconfirmation',
                        dest='skipConfirmation', action='store_true')

    args = parser.parse_args()
    return args


def parse_config_file(configFilePath):
    with open(configFilePath, 'r') as f:
        doc = xmltodict.parse(f.read())
    root = doc['config']
    baseDirPath = root['baseDirectoryPath'].strip()
    rawMatchPatterns = root['matchPatterns']
    ignoreMatchedDirSubtree = root.get('ignoreMatchedDirSubtree', 'false')
    ignoreMatchedDirSubtree = ignoreMatchedDirSubtree.lower() == 'true'

    if isinstance(root['operators']['operator'], list):
        operators = root['operators']['operator']
    else:
        operators = []
        operators.append(root['operators']['operator'])

    return baseDirPath, rawMatchPatterns, operators, ignoreMatchedDirSubtree


def load_operators(operatorsConfigurations):
    operators = []
    for opConf in operatorsConfigurations:
        opClass = getattr(__import__(opConf['@module']), opConf['@name'])
        opInstance = opClass(opConf)
        opInstance.params = opConf
        operators.append(opInstance)

    return operators


if __name__ == '__main__':
    main()
