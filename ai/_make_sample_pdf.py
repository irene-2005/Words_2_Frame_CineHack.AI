from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from pathlib import Path

base = Path(__file__).resolve().parent
out = base / 'sample.pdf'

sample_text = '''INT. CITY STREET - DAY
A car CHASE ends in an EXPLOSION. The crowd scatters.
JOHN
I need to get to the boat.
EXT. WAREHOUSE - NIGHT
A big FIGHT breaks out. PEOPLE RUN and SHOOT.
'''

c = canvas.Canvas(str(out), pagesize=letter)
textobj = c.beginText(40, 700)
for line in sample_text.splitlines():
    textobj.textLine(line)
c.drawText(textobj)
c.save()

print('Wrote sample PDF to', out)
