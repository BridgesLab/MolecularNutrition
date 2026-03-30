# Teach latexmk how to generate the nomenclature .nls file from the .nlo file.
# Without this, latexmk does not know to run makeindex on .nlo files,
# so \printnomenclature produces a blank page.
add_cus_dep('nlo', 'nls', 0, 'makenls');
sub makenls {
    system("makeindex \"$_[0].nlo\" -s nomencl.ist -o \"$_[0].nls\"");
}
