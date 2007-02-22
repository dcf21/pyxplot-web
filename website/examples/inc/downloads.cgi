#!/usr/bin/perl

# Produce a list of downloadable files in the current directory

use warnings;
use strict;

# Two classes of files to make available.
# Class 1 we label by the extension only.
# Class 2 we glob and label by the filename

my @files1 = ('script.ppl', 'output.eps', 'output.png');
my @files2 = ('*.dat');

# Get all the HTML shit in here
our $downloadhtml = <<"EOF";
			<div class="exampledownload">
				<a href="%FILENAME%">%TEXT%</a>
				<div class="exampledownloadsize">
					%SIZE%
				</div>
			</div>
EOF

print "Content-type: text/html\n\n";

# Deal with the first set of files
foreach my $file (@files1) {
	checkExists($file);
	my $size = fileSize($file);
	my $extension = fileExtension($file);
	my $html = interpolateHtml($file, $extension, $size);
	print $html;
}

# Deal with the second set of files
foreach my $glob (@files2) {
   foreach my $file (glob $glob) {
		checkExists($file);
		my $size = fileSize($file);
		my $html = interpolateHtml($file, $file, $size);
		print $html;
	}
}

# Check that a file exists
sub checkExists {
	my $file = shift @_;
	unless ( -e $file ) {
	   die "File $file does not exist!\n";
	}
}

# Get the size of a file
sub fileSize {
	my $file = shift @_;
	open LS, "ls -lh $file|" or die "Failed to ls $file";
	my $ls = <LS>;
	close LS;
	my @ls = split " ", $ls;
	return $ls[4];
}

# Get a file's extension
sub fileExtension {
	my $file = shift @_;
	$file =~ /(\.\w+)$/;
	return $1;
}


# Interpolate values into html
sub interpolateHtml {
	my ($file, $name, $size) = @_;
	my $html = $downloadhtml;
	$html =~ s/%FILENAME%/$file/;
	$html =~ s/%TEXT%/$name/;
	$html =~ s/%SIZE%/$size/;
	return $html;
}
