#!/usr/bin/python3

'''
This script converts markdown documents into HTML documents.

Each function has its own doctests (just like in lab),
and you should begin this assignment by solving the doctests (just like in lab).
This will let you focus on completing just one small piece of the assignment at a time and not get lost in the "big picture".
Then, once all of these small pieces are complete,
the entire assignment should just work "magically".

Dividing up a large project into smaller "doctestable" components is more of an art than a science.
As you get more experience programming,
you'll slowly learn how to divide up your code this way for yourself.
This is one of the main skills that separates senior programmers from junior programmers.

There's a handful of coding techniques in here that we haven't covered in class and you're not expected to understand.
This is intentional.
An important skill when learning a programming language is being able to work in an environment that you don't 100% understand.
(Again, this is similar to when learning a human language...
when we learn a new human languages,
we won't 100% understand everything in the new language,
but we still have to be able to work with the parts that we do understand.)

WARNING:
Recall that the technology policy places no restriction on your ability to use AI tools like ChatGPT or copilot.
Many of the simpler functions below can be solved directly with the tools.
But I strongly encourage you not to just copy/paste solutions from these tools into the homework.
The more complex functions below cannot be solved by current AI tools.
If you use AI as a crutch to solve the simple problems for you,
you will not be able to solve the more difficult problems.
'''

from markdown_compiler import (
    convert_file
)


def main():
    # process command line arguments
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_file', required=True)
    # FIXME:
    # to get the command_lines test to pass,
    # you will need to uncomment the line below;
    # then add the args.add_css variable as a parameter to convert_file
    parser.add_argument('--add_css', action='store_true')
    args = parser.parse_args()

    # call the main function
    convert_file(args.input_file, args.add_css)


if __name__ == '__main__':
    main()



