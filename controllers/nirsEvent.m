function datlog = nirsEvent(eventAudioKey, eventIdNirs, eventDisplayString, instructions, datlog, Oxysoft, nirsPresent)
    % eventAudioKey: the internal string used to locate audio mp3, or empty
    % if no audio need to be displayed for this event (i.e. trial end)
    %
    % eventIdNirs: the single letter id of the event used to log event in
    % the Oxysoft
    %
    % eventDisplayString: a nicer display string used to print and log in
    % nirs (includign the strating alphabet letter
    %
    % instructions: the map of audioplayer object keyed by the audio key
    % string
    %
    % datlog: the data log struct, used to track start time
    %
    % Oxysoft: the Oxysoft object, to remote connect and log events.
    %
    % nirsPresent: boolean indicating if testing with the instrument
    % Oxysoft present and connected or nos
    %
    
    %Display the current event name and time. Useful if participant is
    %using headphones so we can tell where we are at, but commenting out to
    %limit print statement and speed up runtime
%     disp(eventDisplayString)
%     clock
    
    %         fopen(ss);fclose(ss);
    %if the event doesn't need audio instruction, will skip playing and
    %simply send the event to NIRS.
    if (isKey(instructions, eventAudioKey))
        play(instructions(eventAudioKey));
    end
    %some event might happen without audio cue but log the timing and
    %display anyway.
    datlog.audioCues.start(end+1)=now;
    datlog.audioCues.audio_instruction_message{end+1} = eventDisplayString;

    if nirsPresent
        Oxysoft.WriteEvent(eventIdNirs,eventDisplayString) %FIXME: uncomment        
    end
end