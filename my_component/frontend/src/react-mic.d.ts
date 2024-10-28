declare module 'react-mic' {
     import { Component } from 'react';
   
     export interface ReactMicProps {
       record?: boolean;
       pause?: boolean;
       backgroundColor?: string;
       visualSetting?: 'frequencyBars' | 'sinewave';
       audioBitsPerSecond?: number;
       mimeType?: string;
       onStop?: (recordedBlob: Blob) => void;
       onData?: (recordedBlob: Blob) => void;
       strokeColor?: string;
       className?: string;
       echoCancellation?: boolean;
       autoGainControl?: boolean;
       noiseSuppression?: boolean;
       channelCount?: number;
     }
   
     export class ReactMic extends Component<ReactMicProps> {}
   }
   