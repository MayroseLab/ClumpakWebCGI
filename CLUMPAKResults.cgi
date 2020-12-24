#!/usr/bin/perl -w

use strict;
use warnings;
use CGI;
use CGI::Carp qw(fatalsToBrowser);
use JSON;
use File::Slurp;
use List::Util qw(first);
use List::MoreUtils qw(any  first_index);

use lib "/bioseq/CLUMPAK";
use CLUMPAK_CONSTS_and_Functions;
#use lib "../";

my $query = new CGI;
my $jobId = $query->param('jobId');

my %jsonData;
$jsonData{'errorOccured'} = 0;
$jsonData{'jobId'} = $jobId;

# checking if jobId is valid
if (!($jobId =~ /^[0-9]+\z/))
{
	$jsonData{'errorOccured'} = 1;
	$jsonData{'error'} = "Job $jobId contains invalid characters";
}
else
{
	my $curJobDir = CLUMPAK_CONSTS_and_Functions::RESULTS_LINK."/$jobId";
	my $curJobURL = CLUMPAK_CONSTS_and_Functions::RESULTS_DIR_NON_SECURE_PATH."/$jobId";
	#my $curJobURL = CLUMPAK_CONSTS_and_Functions::RESULTS_DIR_SECURE_PATH."/$jobId";  // the alternative seems to not work well for some users/browsers
	
	# checking if job directory exists
	if (-d $curJobDir)
	{
		my $dataResultsRef = &GetResultsData($jobId, $curJobDir, $curJobURL);
		my %dataResults = %$dataResultsRef;
		
		%jsonData = (%jsonData, %dataResults);
	}
	else
	{
		$jsonData{'errorOccured'} = 1;
	    $jsonData{'error'} = "Job $jobId does not exists.";
	}
}


# parsing return data to json and returnig it to client
my $json = encode_json(\%jsonData);
print $query->header();
print "$json\n";






sub GetResultsData
{
	my ($jobId, $curJobDir, $curJobURL) = @_;
	
	my %jsonData;
	
	$jsonData{'jobId'} = $jobId;
	
	$jsonData{'jobStatus'} = &GetJobStatus($jobId, $curJobDir);
	
	$jsonData{'jobType'} = &GetJobType($curJobDir);
	
	$jsonData{'files'} = &GetOutputFiles($curJobDir, $curJobURL);
	
	$jsonData{'images'} = &GetOutputImages($curJobDir);
	
	my $logText = &ReadFromFile("$curJobDir/".CLUMPAK_CONSTS_and_Functions::LOG_FILE, "");
	$jsonData{'logText'} = $logText;
	
	return \%jsonData;
}

sub GetOutputFiles
{
	my ($curJobDir, $curJobURL) = @_;
	
	my @filesDict;
	
	my $filename = "$curJobDir/".CLUMPAK_CONSTS_and_Functions::OUTPUT_FILES_LIST;
	 
	my @files = &ReadFromFile($filename);
		
	foreach my $file (@files)
    {
			$file =~ s/^\s+//;
			$file =~ s/\s+$//;
			
 			my %curFile;
 			$curFile{'name'} = $file;
			$curFile{'path'} = "$curJobURL/$file";
			
 			
 			push (@filesDict, \%curFile);
	}
	 
    return \@filesDict;
}

sub GetOutputImages
{
	my ($curJobDir) = @_;
	
	my @imagesDict;
	
	my $filename = "$curJobDir/".CLUMPAK_CONSTS_and_Functions::IMAGES_TO_DISPLAY_LIST;
	 
	my @lines = &ReadFromFile($filename);
	
	foreach my $line (@lines)
    {
			$line =~ s/^\s+//;
			$line =~ s/\s+$//;
			
			my @parts = split("\t", $line);

			my $file = pop(@parts);
			my $url = "$curJobDir/$file";
			
			
 			my %curImg;
 			$curImg{'titleParts'} = \@parts;
 			$curImg{'url'} = $url;
 			
 			push (@imagesDict, \%curImg);
	}
	 
    return \@imagesDict;
}

sub GetJobType
{
	my ($curJobDir) = @_;
	
	my $jobTypeFile = "$curJobDir/".CLUMPAK_CONSTS_and_Functions::JOB_TYPE_FILE;
	
	my $jobType = &ReadFromFile($jobTypeFile,'unknown');
	
	return $jobType;
}

sub GetJobStatus
{
	my ($jobId, $curJobDir) = @_;
	
	if (&ReadErrorLogFileStatus($curJobDir))
	{
		return 'error';
	}
	else {
		my $jobNumFile = "$curJobDir/".CLUMPAK_CONSTS_and_Functions::QSUB_JOB_NUM_FILE;
		
		my $qsubJobNum = &ReadFromFile($jobNumFile, 0);
		
		if ($qsubJobNum eq "validating") {
			return "validating input files";
		}
		elsif ($qsubJobNum) 
	 	{
			my $qstatCmd = 'ssh bioseq@powerlogin qstat'; #'ssh bioseq@lecs2 qstat';
			my $qstatCmdResponse = `$qstatCmd`;	
			
			
			my @responseLines = split("\n", $qstatCmdResponse);
			
			if (!any { /$qsubJobNum/ } @responseLines)
			{
					return 'finished';
			}
			else
			{
				my $jobNumLine = first { /$qsubJobNum/ } @responseLines;
			
				my @jobNumLines = split(" ",$jobNumLine);
				
				my $jobStatus = $jobNumLines[4];
				
				$jobStatus = lc($jobStatus);
				
				if (index($jobStatus, 'e') != -1)
				{
		    		return 'error';
				}
				elsif (index($jobStatus, 'r') != -1 || index($jobStatus, 't') != -1)
				{
					return 'running';
				}
				elsif (index($jobStatus, 'q') != -1 || index($jobStatus, 'w') != -1)
				{
#					my $log = "$curJobDir/".CLUMPAK_CONSTS_and_Functions::LOG_FILE;
#					&WriteToFileWithTimeStamp($log, "Job $jobId is waiting in queue.");
#					
					return 'waiting in queue';
				}
				elsif (index($jobStatus, 'c') != -1)
				{
					return 'finished';
				}
				else
				{
					return $jobStatus;
				}
			}
	 	}
	}
	
 	return 'unknown';
}

sub ReadErrorLogFileStatus
{
	my ($curJobDir) = @_;
	
	my $errLog = "$curJobDir/".CLUMPAK_CONSTS_and_Functions::ERROR_STATUS_LOG_FILE;

	my $errStatus = ReadFromFile($errLog, 0);
	
	return $errStatus;
}



