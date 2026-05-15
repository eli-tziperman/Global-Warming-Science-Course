#!/bin/bash
# echo commands to screen:
set -o verbose
# Any subsequent commands which fail will cause the shell script to
# exit immediately:
set -e

dir=/Users/eli/public_html/eli/Courses/EPS101
myrsync dry-run $dir/index.html $dir/lecture-outline.html $dir/image-credits.html $dir/textbook.html $dir/images $dir/js $dir/css ~/Courses/EPS101/open-course-site/
