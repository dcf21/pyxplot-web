#!/usr/bin/perl

# Generate "previous" and "next" navigations buttons

use warnings;
use strict;

# Stupid http shit
print "Content-type: text/html\n\n";

# Get the current working directory
my $cwd = `/bin/pwd`;
chomp $cwd;

# Work out what the number of the current directory is
unless ($cwd =~ /\/([0-9]{2})[a-zA-Z]+$/) {die "Bad directory $cwd\n";}
my $dirnumber = $1;

my ($prevlink, $nextlink);

# Find the dir of the previous number
my $prevnumber = $dirnumber - 1;
if ($prevnumber =~ /^.$/) {$prevnumber = "0$prevnumber";}
my @glob = glob("../$prevnumber*");
if ($#glob > 0) {
	die "Too many directories";
} elsif ($#glob == 0) {
	$prevlink = "<a href=\"$glob[0]\">Previous</a>";
} else {
	$prevlink = "Previous";
}

# And the next number
my $nextnumber = $dirnumber + 1;
if ($nextnumber =~ /^.$/) {$nextnumber = "0$nextnumber";}
@glob = glob("../$nextnumber*");
if ($#glob > 0) {
	die "Too many directories";
} elsif ($#glob == 0) {
	$nextlink = "<a href=\"$glob[0]/\">Next</a>";
} else {
	$nextlink = "Next";
}

# Now spit out some html
my $html = <<"EOF";
         <div class="examplebutton">
         $prevlink
         </div>
			<div class="examplebutton">
			<a href="../">Up</a>
			</div>
         <div class="examplebutton">
         $nextlink
         </div>
EOF
print $html;
