# first_snap: duration in millisecs (or something else) from start of the first video to the first snap
#             must be "guessed" manually by watching the video file and marking the time of the first snap 
#             to synchronize the timestamps with the video files 
def autocut(first_snap: Duration, video_directory: DirectoryPath, timestamp_file: FilePath, output_directory: DirectoryPath):
    videofiles_unsorted = []
    for filepath in directory.getAllFilepaths():
        if isVideoFile(filepath):
            videofiles_unsorted.append(filepath)
    videofiles: [FilePath] = sort(videofiles_unsorted)
    
    video_file_durations: {VideoFile -> (Duration, Duration)} = {}
    previous_end: Duration = 0
    for video_filepath in videofiles:
        video: Video = Video(video_filepath)
        file_start: Duration = previous_end
        file_end: Duration = previous_end + video.duration()
        previous_end = end
        video_file_durations[video_filepath] = (file_start, file_end)

    assert(first_snap <= Video(videofiles[0]).duration())  # First Snap should be in first video File. (Maybe this restriction is not necessary) 
    
    
    cutmarks: [(TimeStamp, Timestamp)] = read_timestamp_file(timestamp_file)  # array of (start,end) tuples, 
    
    (first_snap_timestamp, _) = cutmarks[0]

    counter: int = 0
    for cutmark in cutmarks:
        (start_timestamp, end_timestamp) = cutmark
        start_duration: Duration = convert_to_duration(start_timestamp, first_snap_timestamp, first_snap)
        end_duration: Duration = convert_to_duration(end_timestamp, first_snap_timestamp, first_snap)
        assert(start_duration < end_duration)

        start_video_filepath = ""
        end_video_filepath = "" # maybe the play ends in another video file
        for video_filepath in videofiles:
            (file_start, file_end) = video_file_durations[video_filepath]
            if start_duration >= file_start and start_duration <= file_end:
                # play begins in this video file
                start_video_filepath = video_filepath
            if end_duration >= file_start and end_duration <= file_end:
                # play ends in this video file
                end_video_filepath = end_video_filepath
        
        assert(start_video_filepath != "" and end_video_filepath != "")

        
        if start_video_filepath == end_video_filepath:
             # play begins and ends in the same videofile
             video = Video(start_video_filepath)
             (file_start, _) = video_file_durations[video_filepath]
             playClip = video.subClip(start_duration-file_start, end_duration-file_start)
        else:
            # play ends in another file
            startVideo = Video(start_video_filepath)
            endVideo = Video(end_video_filepath)
            (firstPart_start, _) = video_file_durations[start_video_filepath]
            (secondPart_start, _) = video_file_durations[end_video_filepath]
            firstPart = startVideo.subClip(start_duration-firstPart_start, startVideo.duration) # from start of the play to the end of the first video
            secondPart = endVideo.subClip(0, end_duration-secondPart_start) # from start of the second video to the end of the play
            playClip = firstPart.concatenate(secondPart)

        counter += 1
        filename = counter.to_string_leading_zeros(4) + ".MOV" # filename = vierstellige Zahl, e.g. "0001.MOV"
        playClip.write_to_file(output_directory.extend(filename))




# convert any given timestamp to a duration from the beginning of the game film to the given time
def convert_to_duration(timestamp, first_snap_timestamp, first_snap_duration):
    # `timestamp - first_snap_timestamp` might be negativ for the first snap of the game,
    # if syncTime has been guessed a little bit too late
    offset = max(timestamp - first_snap_timestamp, 0) 
    return first_snap_duration + offset^
    


def read_timestamp_file(filepath):
    # parse CSV/Excel/Spreadsheet to extract tuples of (start, end) timestamps