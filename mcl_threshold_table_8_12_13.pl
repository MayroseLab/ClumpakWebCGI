#!usr/local/bin/perl
use strict;
use warnings;
#$mat_name = $ARGV[0];

my $mat_name = "/groups/itay_mayrose/jonathanm/temp/mcl_test/ClumppPairMatrix";

open (IN, "<$mat_name");
open (OUT, ">$mat_name.out");

my $line;

my $run_number=0;
while ($line=<IN>)
{
	$run_number++;
	chop $line;
	$line =~ s/\s+$//;
	$line =~ s/\s+/\t/g;
	print OUT "$line\n";
}
close IN;
close OUT;

print "number of runs is $run_number\n";

system ("mcl/bin/mcxarray -co 0 -data $mat_name.out -write-data - | mcl-13-158/bin/mcx query -imx - -vary-threshold 0.7/1.0/30  -o $mat_name.table");

open (IN, "<$mat_name.table");

my $final_cutoff;

while ($line=<IN>)
{
	chop $line;
	if ($line=~/cce/ && $line=~/EWmed/)
	{
		chop $line;
		$line=<IN>;  #this is the line ------------, in the next line the table starts
		my $my_index=0;
		$final_cutoff=-1;
		my $prev_cutoff=-1;
		my $final_index=-1;
		while ($line = <IN>)
		{
			$my_index++;
			if ($line =~ /-----/) {exit;}
			$line =~ s/^\s+//;
			my @line_arr=split (/\s+/, $line);
			my $cutoff=$line_arr[14];
			print "$my_index $line\n";
			my $th1=$run_number/2;
			my $th2=10;
			#print "$line_arr[9]-$th1  $line_arr[3]-$th2  ";
			if ($line_arr[3]>$th2 || $line_arr[9]<$th1)
			{
				if ($my_index==1) {
					$final_cutoff = $cutoff;
				}
				else {
					$final_cutoff = $prev_cutoff;
				}
				print "the chosen cutoff is $final_cutoff\n\n";
				last; 
			}
			$prev_cutoff=$cutoff;
			print "\n";
		}		
	}
}

#open (OUT, ">$mat_name.mcl_out");
system ("mcl/bin/mcxarray -co 0 -data $mat_name.out -write-data - | mcl/bin/mcl - -I 2 -tf \'gq($final_cutoff), add(-$final_cutoff)\' -o $mat_name.clusters_output");
#system ("mcl/bin/mcxarray -co 0 -data $mat_name.out -write-data - | mcl/bin/mcl - -I 2 -tf \'gq($final_cutoff), add(-$final_cutoff)\' -aa .co");

