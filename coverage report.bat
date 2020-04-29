cd test
coverage html --omit=*/programming/*,*/_*.py,*/test.py
cd ..
firefox test/htmlcov/index.html