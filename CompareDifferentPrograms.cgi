#!/usr/bin/perl -w

use strict;
use warnings;
use CGI;
use CGI::Carp qw(fatalsToBrowser);
use File::Basename;
use File::Path;
use File::Slurp;

use lib "../";
use lib "/bioseq/CLUMPAK";

use CLUMPAK_CONSTS_and_Functions;
use ValidationTests;
use SmokeTestsMethods;

# this command limits the size of the uploded file
my $maxMB = 100; 
$CGI::POST_MAX = 1024 * 1000 * $maxMB;

my $safe_filename_characters = "a-zA-Z0-9_.-";
my $jobId = $^T;
my $curJobdir = CLUMPAK_CONSTS_and_Functions::RESULTS_DIR_ABSOLUTE_PATH."/$jobId";

my $log = "$curJobdir/".CLUMPAK_CONSTS_and_Functions::LOG_FILE;
my $errLog = "$curJobdir/" . CLUMPAK_CONSTS_and_Functions::ERROR_STATUS_LOG_FILE;

my $query = new CGI;

# checking if submission is allowed
my $smokeTestsFlagVal = &ReadTestsSuccessFlag();

if ($smokeTestsFlagVal == 0) {
	print $query->redirect('/maintenance.html');
	exit(0);
}

# getting inputs from user
my $structureZipFilePath 	= $query->param("structureZipFile");
my $structureZipFilePath2 	= $query->param("structureZipFile2");
my $distructLabelsFile 		= $query->param("distructLabelsFile");
my $email_to_address		= $query->param("inputEmail");
my $drawparamsFile			= $query->param("drawparamsFile");
my $colorsFile				= $query->param("colorsFile");
my $MCL_type				= $query->param("MCL_type");
my $MCL_threshold			= $query->param("MCL_threshold");

#CLUMPP
my $search_method_radioBtn 		= $query->param("search_method_radioBtn");
my $greedy_options_radioBtn 	= $query->param("greedy_options_radioBtn");
#my $CLUMPP_repeats_radioBtn 	= $query->param("CLUMPP_repeats_radioBtn");
my $writeClumppParams 			= $query->param("writeClumppParams");
my $CLUMPP_repeats				= $query->param("CLUMPP_repeats");

my $MCL_MinClusterFraction_radioBtn 	= $query->param("MCL_MinClusterFraction_radioBtn");
my $MCL_MinClusterFraction_threshold	= $query->param("MCL_MinClusterFraction_threshold");

my $inputtype1				= $query->param("inputtype1");
my $inputtype2				= $query->param("inputtype2");
my $populations_file		= $query->param("populations_file");



if ( !$structureZipFilePath )
{
	print $query->header ( );
	print "There was a problem uploading your structure zip (try a smaller file).";
	exit;
} 

# checking zip filename for invalid characters
my ( $name, $path, $extension ) = fileparse ( $structureZipFilePath, '\..*' );
$structureZipFilePath = $name . $extension;
$structureZipFilePath =~ tr/ /_/;
$structureZipFilePath =~ s/[^$safe_filename_characters]//g;

if ( $structureZipFilePath =~ /^([$safe_filename_characters]+)$/ )
{
	$structureZipFilePath = $1;
}
else
{
	die "Filename contains invalid characters";
}

#ofer start structureZipFilePath2
if ( !$structureZipFilePath2 )
{
	print $query->header ( );
	print "There was a problem uploading your structure zip 2(try a smaller file).";
	exit;
} 

# checking zip filename 2 for invalid characters
my ( $name2, $path2, $extension2 ) = fileparse ( $structureZipFilePath2, '\..*' );
$structureZipFilePath2 = $name2 . $extension2;
$structureZipFilePath2 =~ tr/ /_/;
$structureZipFilePath2 =~ s/[^$safe_filename_characters]//g;

if ( $structureZipFilePath2 =~ /^([$safe_filename_characters]+)$/ )
{
	$structureZipFilePath2 = $1;
}
else
{
	die "Filename 2 contains invalid characters";
}
#ofer end


# creating cur job directory
mkpath($curJobdir);

# uploading zip to job directory
my $upload_filehandle = $query->upload("structureZipFile");
my $zipServerLocation = "$curJobdir/$structureZipFilePath";
open ( UPLOADFILE, ">$zipServerLocation" ) or die "$!";
binmode UPLOADFILE;

while ( <$upload_filehandle> )
{
	print UPLOADFILE;
}

close UPLOADFILE;

# ofer uploading zip 2 to job directory
my $upload_filehandle2 = $query->upload("structureZipFile2");
my $zipServerLocation2 = "$curJobdir/$structureZipFilePath2";
open ( UPLOADFILE, ">$zipServerLocation2" ) or die "$!";
binmode UPLOADFILE;

while ( <$upload_filehandle2> )
{
	print UPLOADFILE;
}

close UPLOADFILE;



# building perl script command
my $serverName = CLUMPAK_CONSTS_and_Functions::SERVER_NAME;
my $cmd = "cd /bioseq/$serverName/;perl CompareDifferentPrograms.pl --id $jobId --dir $curJobdir --firstfile $zipServerLocation --secondfile $zipServerLocation2";
# uploading distruct labels
my $labelsServerLocation;

if ( $distructLabelsFile )
{
	# checking zip filename for invalid characters
	my ( $name, $path, $extension ) = fileparse ( $distructLabelsFile, '\..*' );
	$distructLabelsFile = $name . $extension;
	$distructLabelsFile =~ tr/ /_/;
	$distructLabelsFile =~ s/[^$safe_filename_characters]//g;
	
	if ( $distructLabelsFile =~ /^([$safe_filename_characters]+)$/ )
	{
		$distructLabelsFile = $1;
	}
	else
	{
		die "Filename contains invalid characters";
	}

	# uploading zip to job directory
	my $distruct_upload_filehandle = $query->upload("distructLabelsFile");
	$labelsServerLocation = "$curJobdir/$distructLabelsFile";
	open ( distruct_UPLOADFILE, ">$labelsServerLocation" ) or die "$!";
	binmode distruct_UPLOADFILE;
	
	while ( <$distruct_upload_filehandle> )
	{
		print distruct_UPLOADFILE;
	}
	
	close distruct_UPLOADFILE;
	
	# adding label file to command
	$cmd = $cmd." --labels $labelsServerLocation";
}

# uploading drawparamsFile 
if ( $drawparamsFile )
{
	# checking zip filename for invalid characters
	my ( $name, $path, $extension ) = fileparse ( $drawparamsFile, '\..*' );
	my $FilePath = $name . $extension;
	$FilePath =~ tr/ /_/;
	$FilePath =~ s/[^$safe_filename_characters]//g;
	
	if ( $FilePath =~ /^([$safe_filename_characters]+)$/ )
	{
		$FilePath = $1;
	}
	else
	{
		die "Filename contains invalid characters";
	}

	# uploading zip to job directory
	my $upload_filehandle = $query->upload("drawparamsFile");
	my $ServerLocation = "$curJobdir/$drawparamsFile";
	open ( UPLOADFILE, ">$ServerLocation" ) or die "$!";
	binmode UPLOADFILE;
	
	while ( <$upload_filehandle> )
	{
		print UPLOADFILE;
	}
	
	close UPLOADFILE;
	
	# adding label file to command
	$cmd = $cmd." --drawparams $ServerLocation";
}

# uploading colorsFile 
if ( $colorsFile )
{
	# checking zip filename for invalid characters
	my ( $name, $path, $extension ) = fileparse ( $colorsFile, '\..*' );
	my $FilePath = $name . $extension;
	$FilePath =~ tr/ /_/;
	$FilePath =~ s/[^$safe_filename_characters]//g;
	
	if ( $FilePath =~ /^([$safe_filename_characters]+)$/ )
	{
		$FilePath = $1;
	}
	else
	{
		die "Filename contains invalid characters";
	}

	# uploading zip to job directory
	my $upload_filehandle = $query->upload("colorsFile");
	my $ServerLocation = "$curJobdir/$colorsFile";
	open ( UPLOADFILE, ">$ServerLocation" ) or die "$!";
	binmode UPLOADFILE;
	
	while ( <$upload_filehandle> )
	{
		print UPLOADFILE;
	}
	
	close UPLOADFILE;
	
	# adding label file to command
	$cmd = $cmd." --colors $ServerLocation";
}

# always write inputtype to cmd
$cmd = $cmd." --firstinputtype $inputtype1";
$cmd = $cmd." --secondinputtype $inputtype2";


# uploading populations_file 
my $populationsfileServerLocation;

if ( $populations_file )
{
	# checking zip filename for invalid characters
	my ( $name, $path, $extension ) = fileparse ( $populations_file, '\..*' );
	my $FilePath = $name . $extension;
	$FilePath =~ tr/ /_/;
	$FilePath =~ s/[^$safe_filename_characters]//g;
	
	if ( $FilePath =~ /^([$safe_filename_characters]+)$/ )
	{
		$FilePath = $1;
	}
	else
	{
		die "Filename contains invalid characters";
	}

	# uploading zip to job directory
	my $upload_filehandle = $query->upload("populations_file");
	$populationsfileServerLocation = "$curJobdir/$populations_file";
	open ( UPLOADFILE, ">$populationsfileServerLocation" ) or die "$!";
	binmode UPLOADFILE;
	
	while ( <$upload_filehandle> )
	{
		print UPLOADFILE;
	}
	
	close UPLOADFILE;
	
	# adding to command
	$cmd = $cmd." --indtopop $populationsfileServerLocation";
}

#CLUMPP
if ( $writeClumppParams eq "true" )
{
	$cmd = $cmd." --clumppsearchmethod $search_method_radioBtn";	
	if ( ($search_method_radioBtn eq "2") or ($search_method_radioBtn eq "3") )
	{
		$cmd = $cmd." --clumppgreedyoption $greedy_options_radioBtn";
		#if ( $greedy_options_radioBtn eq "2" )
		#{
			$cmd = $cmd." --clumpprepeats $CLUMPP_repeats";			
		#}
	}
}

if ( $MCL_type eq "UserDefined" )
{
	$cmd = $cmd." --mclthreshold $MCL_threshold";	
}

if ( $MCL_MinClusterFraction_radioBtn eq "UserDefined" )
{
	$cmd = $cmd." --mclminclusterfraction $MCL_MinClusterFraction_threshold";	
}

write_file("$curJobdir/".CLUMPAK_CONSTS_and_Functions::JOB_TYPE_FILE, "Compare Different Programs");
write_file("$curJobdir/".CLUMPAK_CONSTS_and_Functions::QSUB_JOB_NUM_FILE, "validating");

my $validationLog = "$curJobdir/validation.OU";

# send 1st email to user
`perl sendFirstEmail.pl $email_to_address $jobId`;


my $pid = fork();
if( $pid == 0 ){
	# this code runs async
	open STDIN,  '<', '/dev/null';
    open STDOUT, '>', $validationLog; # point to /dev/null or to a log file
    open STDERR, '>&STDOUT';
    
     # log
	use POSIX qw(strftime);
	my $logPath = CLUMPAK_CONSTS_and_Functions::LOG_DIR_ABSOLUTE_PATH; 
	$logPath = $logPath.CLUMPAK_CONSTS_and_Functions::COMPARE_PROGRAMS_LOG;
	my $date = strftime('%F %H:%M:%S', localtime);
	&WriteToFile( $logPath, "$email_to_address\t$date\t$jobId");

	# building load perl module cmd
	my $perlModule =  CLUMPAK_CONSTS_and_Functions::PERL_MODULE_TO_LOAD; 
	my $loadModuleCmd = "module load $perlModule";
    
    #creating shell script file for lecs
	my $qsub_script = "$curJobdir/qsub.sh";
	open (QSUB_SH,">$qsub_script");
	  
	#print QSUB_SH "#!/bin/tcsh\n";
	#print QSUB_SH '#$ -N ', "$serverName"."_$jobId\n";
	#print QSUB_SH '#$ -S /bin/tcsh', "\n";
	#print QSUB_SH '#$ -cwd', "\n";
	#print QSUB_SH '#$ -l bioseq', "\n";
	#print QSUB_SH '#$ -e ', "$curJobdir", '/$JOB_NAME.$JOB_ID.ER', "\n";
	#print QSUB_SH '#$ -o ', "$curJobdir", '/$JOB_NAME.$JOB_ID.OU', "\n";
	#print QSUB_SH "$loadModuleCmd\n";
	#print QSUB_SH "hostname;\n"; # for debug - to know which node ran the job	
	#print QSUB_SH "$cmd\n";
	
	print QSUB_SH "#!/bin/bash\n";
	print QSUB_SH '#PBS -N ', "$serverName"."_$jobId","\n";
	print QSUB_SH '#PBS -r y',"\n";
	print QSUB_SH '#PBS -v PBS_O_SHELL=bash,PBS_ENVIRONMENT=PBS_BATCH',"\n";
	print QSUB_SH '#PBS -q lifesciweb',"\n";
	print QSUB_SH '#PBS -e ', "$curJobdir", '/', "\n";
	print QSUB_SH '#PBS -o ', "$curJobdir", '/', "\n";
	print QSUB_SH "$loadModuleCmd\n";
	print QSUB_SH "hostname;\n"; # for debug - to know which node ran the job
	print QSUB_SH "$cmd\n";
	

	# this will send results ready email to user 
	my $cmdEmail = "cd /bioseq/$serverName/;perl sendLastEmail.pl --toEmail $email_to_address --id $jobId;";
	print QSUB_SH "$cmdEmail\n";
	
	close (QSUB_SH);
    
	#validation Tests
	&WriteToFileWithTimeStamp($log, "Running validation tests on input files");
	
	my $validationTestsDir = "$curJobdir/ValidationTests";
	mkpath($validationTestsDir);
	
	eval {
		do {
	    	print "Validating CLUMPAK input..\n";
	    	print "Compare cmd:\n$cmd\n\n";
			&CompareDifferentProgramsValidationTests($zipServerLocation, $inputtype1, $zipServerLocation2, $inputtype2, $jobId, $validationTestsDir, 
														$labelsServerLocation, $populationsfileServerLocation, $CLUMPP_repeats, $search_method_radioBtn, $greedy_options_radioBtn);
			print "Finished validating..\n";
		};
	};
	if ($@) {
		my $errMsg = ( split( " at", $@ ) )[0];
	
		&WriteToFileWithTimeStamp( $log, "error occurred - $errMsg." );
		&WriteToFile( $errLog, $@ );
	}
	else {
		&WriteToFileWithTimeStamp($log, "Finished validating - Submitting job to queue");
		rmtree($validationTestsDir);
				
		#my $qsubCmd =  'ssh bioseq@lecs2 qsub '."$qsub_script";
		my $qsubCmd =  'ssh bioseq@powerlogin qsub '."$qsub_script";
		
		my 	$qsubJobNum = "NONE";
		my $ans = `$qsubCmd`;
		if ($ans =~ /(\d+)/)
		{
			$qsubJobNum = $1;
		}
		
		write_file("$curJobdir/".CLUMPAK_CONSTS_and_Functions::QSUB_JOB_NUM_FILE, $qsubJobNum);
		
		&WriteToFileWithTimeStamp($log, "Job $jobId was submitted to queue.");
		
		# send 1st email to user
		#`perl sendFirstEmail.pl $email_to_address $jobId`;
	}
		
	exit 0;
}

# redirecting client to results page
my $redirectedURL = CLUMPAK_CONSTS_and_Functions::RESULTS_PAGE_URL."?jobId=";
$redirectedURL = $redirectedURL.$jobId;
print $query->redirect($redirectedURL);
