from PIL import Image, ImageChops
A=Image.open('claim_screen.png').convert('RGB')
B=Image.open('claim_after_click.png').convert('RGB')
D=ImageChops.difference(A,B)
print('diff bbox:', D.getbbox())
print('changed' if D.getbbox() else 'same')
