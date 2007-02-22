#!/usr/bin/perl

# Obligatory header
print "Content-type: text/html\n\n";

# Obtain a listing of all the subdirectories
my @ls;
open LS, "/bin/ls -F|" or die "Failed to ls";
while (<LS>) {
	chomp;
	# Check for directoryness
   if (/^(.*)\/$/) {
	   push @ls, $1;
	}
}
close LS;

# Produce the relevent entry for each one 
foreach my $dir (@ls) {
	print "<h3>\n";
	print '<a href="' . $dir . '/">';
	
	# Read in the heading, digest it and spit it out again
	open HEADING, "$dir/heading.shtml" or die "Failed to read heading $dir/heading.shtml";
	my $heading = <HEADING>;
	close HEADING;
	unless ($heading =~ /value="(.*)" -->/) {die "Failed to parse heading $heading\n"}
	print $1;

	print <<"EOF";
</a>
</h3>
<p>
EOF
   # Read in description and spit it out again
	open DESC, "$dir/description.shtml" or die "Failed to read description $dir/description.shtml";
	foreach (<DESC>) {print;}
	close DESC;
	
	print <<"EOF";
</p>

EOF
   
}



