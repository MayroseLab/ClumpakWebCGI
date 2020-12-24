#!/usr/bin/perl -w

use strict;
use warnings;
use CGI;
use CGI::Carp qw(fatalsToBrowser);

# use this cgi to redirect client to a maintenance page
my $query = new CGI;
print $query->redirect('http://clumpak.tau.ac.il/maintenance.html');
exit(0);