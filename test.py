from generator.generator import generate
from executor.executor import execute
import sys
import test.testcase
import unit_test.testcase


def test_file(filename, print_exception=True):
    """
    测试filename代码的编译与执行
    :param filename:
    :param print_exception: 是否打印异常
    :return: 是否正确编译与执行
    """
    output_filename = filename.split('.')[0]+".ll"

    try:
        generate_result = generate(input_filename=filename, output_filename=output_filename)
    except Exception as e:
        print("generate", filename, "failed.")
        if print_exception:
            print(e)
        return False

    if not generate_result:
        print("generate", filename, "failed.")
        return False
    else:
        try:
            execute_result = execute(output_filename)
        except Exception as e:
            print("execute", output_filename, "failed.")
            if print_exception:
                print(e)
            return False

        print(output_filename, "exited with code", execute_result)
        return True


def test_files(filenames, print_exception=False):
    """
    测试文件列表filenames中的所有文件
    :param filenames:
    :param print_exception: 是否打印异常
    :return: None
    """
    success_numbers = 0
    fail_numbers = 0
    for filename in filenames:
        if test_file(filename, print_exception):
            success_numbers += 1
        else:
            fail_numbers += 1
        print()
    print("Test Results:", success_numbers, "success,", fail_numbers, "fails")


if __name__ == '__main__':
    if len(sys.argv) == 2:
        if sys.argv[1] == "unit":  # 运行单元测试文件
            test_files(filenames=unit_test.testcase.cases(), print_exception=False)
        else:  # 运行某个特定的C文件进行测试
            test_file(filename=sys.argv[1], print_exception=True)
    else:  # 运行测试文件
        test_files(filenames=test.testcase.cases(), print_exception=False)


