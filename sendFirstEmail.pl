#!/usr/bin/perl
 
 
#print "$ARGV[0]\n";

 
$to 		= $ARGV[0];
$jobId 		= $ARGV[1];
$from 		= 'evolseq@tauex.tau.ac.il';
$subject	= "Your CLUMPAK job# $jobId is being processed";

$resultsLink = 'http://clumpak.tau.ac.il/results.html?jobId=';
$resultsLink = $resultsLink."$jobId";

$message   = "Dear CLUMPAK user,\n\n";
$message  .= "Your CLUMPAK job# $jobId is being processed.\n";
$message  .= "We will email you again when processing will finish.\n\n";
$message  .= "View your job\'s progress and results here:\n";
$message  .= "$resultsLink\n\n";

$message  .= "Thanks you for using CLUMPAK!\n";
$message  .= "CLUMPAK team.\n";

open(MAIL, "|/usr/sbin/sendmail -t");
 
# Email Header
print MAIL "To: $to\n";
print MAIL "From: $from\n";
print MAIL "Subject: $subject\n\n";

# Email Body
print MAIL $message;

close(MAIL);
print "Email Sent Successfully to: $to\n";

