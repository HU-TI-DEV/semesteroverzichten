call overzichtgenerator\venv\Scripts\activate
python overzichtgenerator\scripts\LeerdoelenkaartenGenerator.py
git filter-repo --path docs --invert-paths
git stage -A
git commit -m "render"
git push --force --all
pause
