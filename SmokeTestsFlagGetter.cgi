#!/usr/bin/perl -w

use strict;
use warnings;
use CGI;
use CGI::Carp qw(fatalsToBrowser);
use JSON;


use lib "/bioseq/CLUMPAK";
use lib "../";

use CLUMPAK_CONSTS_and_Functions;
use SmokeTestsMethods;

my $query = new CGI;

my $smokeTestsFlagVal = &ReadTestsSuccessFlag();

if ($smokeTestsFlagVal == 1) {
	print $query->header();
	print "true\n";
}
else {
	print $query->header();
	print "false\n";
}
