#!/usr/bin/perl
#

# Scoop up file
open INFILE, "script.ppl" or die "Failed to open script";
@script = <INFILE>;
close INFILE;

# First do an eps
open PPL, "|pyxplot";
print PPL "set term eps\n";
print PPL "set out 'output.eps'\n";
foreach (@script) {
	print PPL $_;
}

# And now a png
print PPL <<"EOF";
set term png\n
set out 'output.png'\n
ref\n
EOF
close PPL;

# Measure the PNG for size

open FILEDATA, "/usr/bin/file output.png|" or die "Failed to run file on output.png\n";
my @filedata = <FILEDATA>;
close FILEDATA;

$filedata[0] =~ m/PNG image data, (\d+) x / or die "Garbled file output $filedata[0]\n";
my $width = $1;

open WIDTH, ">width" or die "Failed to write to width file";
print WIDTH $width;
close WIDTH;
