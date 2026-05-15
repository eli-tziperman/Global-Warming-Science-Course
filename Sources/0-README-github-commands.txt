To set this up in GitHub, I did:

Go to https://github.com/eli-tziperman?tab=repositories
click new
specify name as global-warming-science
specify private
click create repository

Then, locally:

cd ~/Courses/EPS101/Sources/
[remove .git folder if it exists]
git init
git add .
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/eli-tziperman/global-warming-science.git


Start GitHub desktop app and "publish branch" from there
