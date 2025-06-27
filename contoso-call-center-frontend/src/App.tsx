import { useState, useEffect } from 'react'
import { Phone, Settings, Download, FileText, Music, AlertTriangle, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Checkbox } from '@/components/ui/checkbox'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Switch } from '@/components/ui/switch'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Progress } from '@/components/ui/progress'
import { Separator } from '@/components/ui/separator'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion'

interface Scenario {
  id: string
  name: string
  description: string
}

interface AudioSettings {
  sampling_rate: number
  channels: number
  generate_audio: boolean
  save_audio_locally: boolean
}

interface CallGenerationRequest {
  scenarios: string[]
  sentiment: string
  duration: string
  num_calls: number
  audio_settings: AudioSettings
  save_transcripts_locally: boolean
}

interface GeneratedCall {
  id: number
  scenario: string
  transcript_data: {
    transcript: string
    scenario: string
    sentiment: string
    duration: string
    participants: string[]
    synthetic_data: Record<string, any>
    metadata: Record<string, any>
  }
  audio_file_url?: string
}

interface CallGenerationResponse {
  calls: GeneratedCall[]
  total_calls: number
  generation_time: number
}

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function App() {
  const [scenarios, setScenarios] = useState<Scenario[]>([])
  const [selectedScenarios, setSelectedScenarios] = useState<string[]>([])
  const [sentiment, setSentiment] = useState<string>('mixed')
  const [duration, setDuration] = useState<string>('medium')
  const [numCalls, setNumCalls] = useState<number>(5)
  const [generateAudio, setGenerateAudio] = useState<boolean>(true)
  const [saveAudioLocally, setSaveAudioLocally] = useState<boolean>(true)
  const [saveTranscriptsLocally, setSaveTranscriptsLocally] = useState<boolean>(true)
  const [samplingRate, setSamplingRate] = useState<number>(16000)
  const [channels, setChannels] = useState<number>(1)
  const [isGenerating, setIsGenerating] = useState<boolean>(false)
  const [generatedCalls, setGeneratedCalls] = useState<GeneratedCall[]>([])
  const [generationProgress, setGenerationProgress] = useState<number>(0)
  const [error, setError] = useState<string>('')

  useEffect(() => {
    fetchScenarios()
  }, [])

  const fetchScenarios = async () => {
    try {
      const response = await fetch(`${API_URL}/scenarios`)
      const data = await response.json()
      setScenarios(data.scenarios)
    } catch (err) {
      setError('Failed to load scenarios')
    }
  }

  const handleScenarioChange = (scenarioId: string, checked: boolean) => {
    if (checked) {
      setSelectedScenarios([...selectedScenarios, scenarioId])
    } else {
      setSelectedScenarios(selectedScenarios.filter(id => id !== scenarioId))
    }
  }

  const generateCalls = async () => {
    if (selectedScenarios.length === 0) {
      setError('Please select at least one scenario')
      return
    }

    setIsGenerating(true)
    setError('')
    setGenerationProgress(0)

    const request: CallGenerationRequest = {
      scenarios: selectedScenarios,
      sentiment,
      duration,
      num_calls: numCalls,
      audio_settings: {
        sampling_rate: samplingRate,
        channels,
        generate_audio: generateAudio,
        save_audio_locally: saveAudioLocally
      },
      save_transcripts_locally: saveTranscriptsLocally
    }

    try {
      const response = await fetch(`${API_URL}/generate-calls`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(request)
      })

      if (!response.ok) {
        throw new Error('Failed to generate calls')
      }

      const data: CallGenerationResponse = await response.json()
      setGeneratedCalls(data.calls)
      setGenerationProgress(100)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate calls')
    } finally {
      setIsGenerating(false)
    }
  }

  const downloadTranscript = (call: GeneratedCall) => {
    const content = `Contoso Medical Call Center - Call #${call.id}
Generated: ${call.transcript_data.metadata.generated_at}
Scenario: ${call.scenario}
Sentiment: ${call.transcript_data.sentiment}
Duration: ${call.transcript_data.duration}

TRANSCRIPT:
${call.transcript_data.transcript}

CALL METADATA:
${JSON.stringify(call.transcript_data.synthetic_data, null, 2)}
`
    
    const blob = new Blob([content], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `call_${call.id}_transcript.txt`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const downloadAllTranscripts = () => {
    generatedCalls.forEach(call => downloadTranscript(call))
  }

  const downloadAudio = async (call: GeneratedCall) => {
    if (!call.audio_file_url) return
    
    try {
      const response = await fetch(`${API_URL}${call.audio_file_url}`)
      const blob = await response.blob()
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `call_${call.id}_audio.wav`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    } catch (err) {
      setError('Failed to download audio file')
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Phone className="h-8 w-8 text-blue-600" />
            <h1 className="text-4xl font-bold text-gray-900">
              Contoso Call Center Synthetic Transcript and Audio Generator
            </h1>
          </div>
          
          <Alert className="max-w-4xl mx-auto mb-6">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription className="text-left">
              <strong>DISCLAIMER:</strong> All generated data is synthetic and fictitious. 
              This application is for simulation purposes only and does not contain real PHI or PII data.
            </AlertDescription>
          </Alert>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Configuration Panel */}
          <div className="lg:col-span-2 space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Settings className="h-5 w-5" />
                  Configuration
                </CardTitle>
                <CardDescription>
                  Configure your call generation parameters
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Scenario Selection */}
                <div>
                  <Label className="text-base font-semibold">Scenario Selection</Label>
                  <div className="mt-3 space-y-3">
                    {scenarios.map((scenario) => (
                      <div key={scenario.id} className="flex items-start space-x-3">
                        <Checkbox
                          id={scenario.id}
                          checked={selectedScenarios.includes(scenario.id)}
                          onCheckedChange={(checked) => 
                            handleScenarioChange(scenario.id, checked as boolean)
                          }
                        />
                        <div className="grid gap-1.5 leading-none">
                          <Label
                            htmlFor={scenario.id}
                            className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                          >
                            {scenario.name}
                          </Label>
                          <p className="text-xs text-muted-foreground">
                            {scenario.description}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <Separator />

                {/* Call Parameters */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="sentiment">Sentiment Mix</Label>
                    <Select value={sentiment} onValueChange={setSentiment}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="positive">Positive</SelectItem>
                        <SelectItem value="neutral">Neutral</SelectItem>
                        <SelectItem value="negative">Negative</SelectItem>
                        <SelectItem value="mixed">Mixed (Random)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <Label htmlFor="duration">Call Duration</Label>
                    <Select value={duration} onValueChange={setDuration}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="short">Short (1-3 minutes)</SelectItem>
                        <SelectItem value="medium">Medium (3-7 minutes)</SelectItem>
                        <SelectItem value="long">Long (7-15 minutes)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div>
                  <Label htmlFor="numCalls">Number of calls to generate</Label>
                  <Input
                    id="numCalls"
                    type="number"
                    min="1"
                    max="50"
                    value={numCalls}
                    onChange={(e) => setNumCalls(parseInt(e.target.value) || 1)}
                    className="mt-1"
                  />
                </div>

                <Separator />

                {/* Local File Output Settings */}
                <div>
                  <Label className="text-base font-semibold">Local File Output</Label>
                  <div className="mt-3 space-y-3">
                    <div className="flex items-center space-x-2">
                      <Switch
                        id="saveTranscriptsLocally"
                        checked={saveTranscriptsLocally}
                        onCheckedChange={setSaveTranscriptsLocally}
                      />
                      <Label htmlFor="saveTranscriptsLocally">Save Transcript Files Locally</Label>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Audio Settings */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Music className="h-5 w-5" />
                  Audio Generation
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center space-x-2">
                  <Switch
                    id="generateAudio"
                    checked={generateAudio}
                    onCheckedChange={setGenerateAudio}
                  />
                  <Label htmlFor="generateAudio">Generate Audio Files (.wav)</Label>
                </div>

                {generateAudio && (
                  <div className="flex items-center space-x-2 pl-6">
                    <Switch
                      id="saveAudioLocally"
                      checked={saveAudioLocally}
                      onCheckedChange={setSaveAudioLocally}
                    />
                    <Label htmlFor="saveAudioLocally">Save Audio Files Locally</Label>
                  </div>
                )}

                {generateAudio && (
                  <div className="space-y-4 pl-6 border-l-2 border-blue-200">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <Label htmlFor="samplingRate">Sampling Rate</Label>
                        <Select value={samplingRate.toString()} onValueChange={(value) => setSamplingRate(parseInt(value))}>
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="8000">8 kHz</SelectItem>
                            <SelectItem value="16000">16 kHz</SelectItem>
                            <SelectItem value="32000">32 kHz</SelectItem>
                            <SelectItem value="48000">48 kHz</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>

                      <div>
                        <Label htmlFor="channels">Channels</Label>
                        <Select value={channels.toString()} onValueChange={(value) => setChannels(parseInt(value))}>
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="1">Mono (Recommended)</SelectItem>
                            <SelectItem value="2">Stereo</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>

                    <div className="bg-blue-50 p-4 rounded-lg">
                      <h4 className="font-semibold text-sm mb-2">Audio Specifications:</h4>
                      <ul className="text-xs text-gray-600 space-y-1">
                        <li>• Format: WAV (Microsoft PCM)</li>
                        <li>• Bit Depth: 16-bit</li>
                        <li>• Sampling Rate: {samplingRate / 1000} kHz</li>
                        <li>• Channels: {channels === 1 ? 'Mono' : 'Stereo'}</li>
                        <li>• Bitrate: {channels === 1 ? '256 kbps' : '512 kbps'}</li>
                        <li>• Codec: PCM</li>
                      </ul>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Generation Panel */}
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Generate Calls</CardTitle>
                <CardDescription>
                  Ready to create synthetic call data
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button 
                  onClick={generateCalls} 
                  disabled={isGenerating || selectedScenarios.length === 0}
                  className="w-full"
                  size="lg"
                >
                  {isGenerating ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <Phone className="mr-2 h-4 w-4" />
                      Generate Calls
                    </>
                  )}
                </Button>

                {isGenerating && (
                  <div className="mt-4">
                    <Progress value={generationProgress} className="w-full" />
                    <p className="text-sm text-gray-600 mt-2">
                      Generating {numCalls} calls...
                    </p>
                  </div>
                )}

                {error && (
                  <Alert className="mt-4" variant="destructive">
                    <AlertTriangle className="h-4 w-4" />
                    <AlertDescription>{error}</AlertDescription>
                  </Alert>
                )}
              </CardContent>
            </Card>

            {generatedCalls.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>Export Options</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <Button onClick={downloadAllTranscripts} variant="outline" className="w-full">
                    <FileText className="mr-2 h-4 w-4" />
                    Download All Transcripts
                  </Button>
                  {generateAudio && generatedCalls.some(call => call.audio_file_url) && (
                    <Button 
                      onClick={() => generatedCalls.forEach(call => call.audio_file_url && downloadAudio(call))} 
                      variant="outline" 
                      className="w-full"
                    >
                      <Music className="mr-2 h-4 w-4" />
                      Download All Audio Files
                    </Button>
                  )}
                </CardContent>
              </Card>
            )}
          </div>
        </div>

        {/* Results Section */}
        {generatedCalls.length > 0 && (
          <Card className="mt-8">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5" />
                Generated Calls ({generatedCalls.length})
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">{generatedCalls.length}</div>
                  <div className="text-sm text-gray-600">Total Calls</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">
                    {new Set(generatedCalls.map(call => call.scenario)).size}
                  </div>
                  <div className="text-sm text-gray-600">Scenarios Used</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-600">
                    {generatedCalls.filter(call => call.audio_file_url).length}
                  </div>
                  <div className="text-sm text-gray-600">Audio Files</div>
                </div>
              </div>

              <Accordion type="single" collapsible className="w-full">
                {generatedCalls.map((call) => (
                  <AccordionItem key={call.id} value={`call-${call.id}`}>
                    <AccordionTrigger className="text-left">
                      <div className="flex items-center gap-3">
                        <Badge variant="outline">Call #{call.id}</Badge>
                        <span className="font-medium">
                          {scenarios.find(s => s.id === call.scenario)?.name || call.scenario}
                        </span>
                        <Badge variant="secondary">{call.transcript_data.sentiment}</Badge>
                      </div>
                    </AccordionTrigger>
                    <AccordionContent>
                      <Tabs defaultValue="transcript" className="w-full">
                        <TabsList className="grid w-full grid-cols-3">
                          <TabsTrigger value="transcript">Transcript</TabsTrigger>
                          <TabsTrigger value="details">Details</TabsTrigger>
                          <TabsTrigger value="actions">Actions</TabsTrigger>
                        </TabsList>
                        
                        <TabsContent value="transcript" className="mt-4">
                          <Textarea
                            value={call.transcript_data.transcript}
                            readOnly
                            className="min-h-[300px] font-mono text-sm"
                          />
                        </TabsContent>
                        
                        <TabsContent value="details" className="mt-4">
                          <div className="space-y-4">
                            <div className="grid grid-cols-2 gap-4 text-sm">
                              <div>
                                <strong>Duration:</strong> {call.transcript_data.duration}
                              </div>
                              <div>
                                <strong>Word Count:</strong> {call.transcript_data.metadata.word_count}
                              </div>
                              <div>
                                <strong>Participants:</strong> {call.transcript_data.participants.join(', ')}
                              </div>
                              <div>
                                <strong>Generated:</strong> {new Date(call.transcript_data.metadata.generated_at).toLocaleString()}
                              </div>
                            </div>
                            
                            <div>
                              <strong className="text-sm">Synthetic Data:</strong>
                              <pre className="mt-2 bg-gray-50 p-3 rounded text-xs overflow-auto">
                                {JSON.stringify(call.transcript_data.synthetic_data, null, 2)}
                              </pre>
                            </div>
                          </div>
                        </TabsContent>
                        
                        <TabsContent value="actions" className="mt-4">
                          <div className="flex gap-3">
                            <Button onClick={() => downloadTranscript(call)} variant="outline">
                              <Download className="mr-2 h-4 w-4" />
                              Download Transcript
                            </Button>
                            {call.audio_file_url && (
                              <Button onClick={() => downloadAudio(call)} variant="outline">
                                <Music className="mr-2 h-4 w-4" />
                                Download Audio
                              </Button>
                            )}
                          </div>
                        </TabsContent>
                      </Tabs>
                    </AccordionContent>
                  </AccordionItem>
                ))}
              </Accordion>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}

export default App
