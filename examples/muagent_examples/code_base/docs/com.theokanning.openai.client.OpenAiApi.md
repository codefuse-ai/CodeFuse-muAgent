
> com.theokanning.openai.client.OpenAiApi

Bases: None

The `OpenAiApi` interface provides a set of methods for interacting with the OpenAI API. This includes methods for listing, retrieving, creating, and deleting various resources such as models, completions, edits, embeddings, files, fine-tuning jobs, images, audio transcriptions, translations, and moderations. It also includes methods for retrieving account information and billing usage.



<br>
> createFineTuningJob

| Column Name | Content |
|-----------------|-----------------|
| Parameters   | request(FineTuningJobRequest)-The request for creating a fine-tuning job. |
| Returns   | This method returns a `Single` object that wraps the `FineTuningJob` object. This `FineTuningJob` object represents the fine-tuning job that has been created. |
| Return type   | `Single&lt;FineTuningJob&gt;` |

<br>
> createImageEdit

| Column Name | Content |
|-----------------|-----------------|
| Parameters   | requestBody(RequestBody)-The request body containing the details for the image edit. |
| Returns   | The method returns an instance of `Single&lt;ImageResult&gt;`. This represents the result of the image edit creation operation. |
| Return type   | `Single&lt;ImageResult&gt;` |

<br>
> deleteFile

| Column Name | Content |
|-----------------|-----------------|
| Parameters   | file_id(String)-The unique identifier of the file to be deleted. |
| Returns   | This method returns a `Single` observable containing the result of the delete operation. If the operation is successful, the `DeleteResult` object will contain the details of the deletion. |
| Return type   | `Single&lt;DeleteResult&gt;` |

<br>
> listFineTunes

| Column Name | Content |
|-----------------|-----------------|
| Parameters   |  |
| Returns   | This method returns a `Single` reactive type that emits an `OpenAiResponse` object containing a list of `FineTuneResult` objects. Each `FineTuneResult` object represents the result of a fine-tuning operation. |
| Return type   | `Single&lt;OpenAiResponse&lt;FineTuneResult&gt;&gt;` |

<br>
> uploadFile

| Column Name | Content |
|-----------------|-----------------|
| Parameters   | purpose(RequestBody)-The purpose of the file being uploaded.
file(MultipartBody.Part)-The file to be uploaded. |
| Returns   | This method returns a `Single` object that emits the `File` object once the file has been uploaded successfully. |
| Return type   | Single&lt;File&gt; |

<br>
> createCompletion

| Column Name | Content |
|-----------------|-----------------|
| Parameters   | request(CompletionRequest)-The request object that contains the parameters for the completion creation. |
| Returns   | The method returns a `Single` object that wraps the `CompletionResult` object. The `CompletionResult` object contains the result of the completion creation. |
| Return type   | `Single&lt;CompletionResult&gt;` |

<br>
> createImage

| Column Name | Content |
|-----------------|-----------------|
| Parameters   | request(CreateImageRequest)-The request object containing the details needed to create an image. |
| Returns   | This method returns the result of the image creation operation. |
| Return type   | `Single&lt;ImageResult&gt;` |

<br>
> getEngines

| Column Name | Content |
|-----------------|-----------------|
| Parameters   |  |
| Returns   | This method returns a `Single` reactive type that emits an `OpenAiResponse` object containing a list of `Engine` objects. Each `Engine` object represents an engine available in the OpenAI API. |
| Return type   | `Single&lt;OpenAiResponse&lt;Engine&gt;&gt;` |

<br>
> retrieveFile

| Column Name | Content |
|-----------------|-----------------|
| Parameters   | file_id(String)-The unique identifier of the file to be retrieved. |
| Returns   | This method returns a `Single` object that contains the file retrieved from the OpenAI server. |
| Return type   | `Single&lt;File&gt;` |

<br>
> retrieveFileContent

| Column Name | Content |
|-----------------|-----------------|
| Parameters   | file_id(String)-The unique identifier of the file whose content is to be retrieved. |
| Returns   | This method returns the content of the file identified by the provided `file_id`. The content is returned as a `Single` reactive stream of `ResponseBody`. |
| Return type   | `Single&lt;ResponseBody&gt;` |

<br>
> retrieveFineTune

| Column Name | Content |
|-----------------|-----------------|
| Parameters   | fine_tuning_job_id(String)-The ID of the fine-tuning job to be retrieved. |
| Returns   | This method returns a `Single` object that contains the details of the fine-tuning job. |
| Return type   | `Single&lt;FineTuningJob&gt;` |

<br>
> createEdit

| Column Name | Content |
|-----------------|-----------------|
| Parameters   | request(EditRequest)-The edit request to be created. |
| Returns   | This method returns the result of the edit request. |
| Return type   | `Single&lt;EditResult&gt;` |

<br>
> createFineTuneCompletion

| Column Name | Content |
|-----------------|-----------------|
| Parameters   | request(CompletionRequest)-The request object that contains the details for the completion. |
| Returns   | This method returns a `Single` object that contains a `CompletionResult` object. This `CompletionResult` object contains the result of the completion request. |
| Return type   | `Single&lt;CompletionResult&gt;` |

<br>
> createImageVariation

| Column Name | Content |
|-----------------|-----------------|
| Parameters   | requestBody(RequestBody)-The request body containing the details required to create an image variation. |
| Returns   | This method returns a `Single` reactive type that emits an `ImageResult` object, which represents the result of the image variation creation operation. |
| Return type   | `Single&lt;ImageResult&gt;` |

<br>
> createTranscription

| Column Name | Content |
|-----------------|-----------------|
| Parameters   | requestBody(RequestBody)-The request body that contains the details for the transcription request. |
| Returns   | This method returns a `Single` observable containing the `TranscriptionResult` from the OpenAI API. |
| Return type   | `Single&lt;TranscriptionResult&gt;` |

<br>
> createTranslation

| Column Name | Content |
|-----------------|-----------------|
| Parameters   | requestBody(RequestBody)-The request body containing the data to be translated. |
| Returns   | This method returns a `Single` reactive-streams `Publisher` that emits a `TranslationResult` object. This object contains the result of the translation request. |
| Return type   | `Single&lt;TranslationResult&gt;` |

<br>
> createModeration

| Column Name | Content |
|-----------------|-----------------|
| Parameters   | request(ModerationRequest)-The moderation request to be created. |
| Returns   | The method returns a `Single` object containing the result of the moderation request. |
| Return type   | `Single&lt;ModerationResult&gt;` |

<br>
> listFiles

| Column Name | Content |
|-----------------|-----------------|
| Parameters   |  |
| Returns   | This method returns an instance of `Single&lt;OpenAiResponse&lt;File&gt;&gt;`. This is a reactive (RxJava) type that emits an `OpenAiResponse` containing a list of `File` objects. |
| Return type   | `Single&lt;OpenAiResponse&lt;File&gt;&gt;` |

<br>
> retrieveFineTuningJob

| Column Name | Content |
|-----------------|-----------------|
| Parameters   | fineTuningJobId(String)-The unique identifier of the fine-tuning job to be retrieved. |
| Returns   | The method returns a `Single` object that contains the `FineTuningJob` associated with the provided fine-tuning job id. |
| Return type   | `Single&lt;FineTuningJob&gt;` |

<br>
> createChatCompletion

| Column Name | Content |
|-----------------|-----------------|
| Parameters   | request(ChatCompletionRequest)-The chat completion request containing the details required to generate a chat message. |
| Returns   | This method returns a `Single` object that emits the result of the chat completion request. The result includes the generated chat message. |
| Return type   | `Single&lt;ChatCompletionResult&gt;` |

<br>
> listFineTuningJobs

| Column Name | Content |
|-----------------|-----------------|
| Parameters   |  |
| Returns   | This method returns a `Single` reactive type that emits an `OpenAiResponse` object containing a list of `FineTuningJob` objects. Each `FineTuningJob` object represents a fine tuning job. |
| Return type   | `Single&lt;OpenAiResponse&lt;FineTuningJob&gt;&gt;` |

<br>
> subscription

| Column Name | Content |
|-----------------|-----------------|
| Parameters   |  |
| Returns   | The method returns the subscription details related to the account. |
| Return type   | `Single&lt;Subscription&gt;` |

<br>
> cancelFineTuningJob

| Column Name | Content |
|-----------------|-----------------|
| Parameters   | fine_tuning_job_id(String)-The ID of the fine tuning job to be cancelled. |
| Returns   | This method returns the `FineTuningJob` that was cancelled. |
| Return type   | `Single&lt;FineTuningJob&gt;` |

<br>
> listModels

| Column Name | Content |
|-----------------|-----------------|
| Parameters   |  |
| Returns   | This method returns a `Single` reactive type that emits an `OpenAiResponse` object containing a list of `Model` objects. Each `Model` object represents a different model available in the OpenAI API. |
| Return type   | `Single&lt;OpenAiResponse&lt;Model&gt;&gt;` |

<br>
> cancelFineTune

| Column Name | Content |
|-----------------|-----------------|
| Parameters   | fine_tuning_job_id(String)-The ID of the fine-tuning job to be cancelled. |
| Returns   | This method returns the `FineTuningJob` that was cancelled. |
| Return type   | `Single&lt;FineTuningJob&gt;` |

<br>
> createEdit

| Column Name | Content |
|-----------------|-----------------|
| Parameters   | request(EditRequest)-The edit request to be sent to the OpenAI API. |
| Returns   | This method returns the result of the edit request. |
| Return type   | `Single&lt;EditResult&gt;` |

<br>
> createEmbeddings

| Column Name | Content |
|-----------------|-----------------|
| Parameters   | request(EmbeddingRequest)-The request body containing the details required to create embeddings. |
| Returns   | This method returns the result of the embedding creation operation. |
| Return type   | Single&lt;EmbeddingResult&gt; |

<br>
> deleteFineTune

| Column Name | Content |
|-----------------|-----------------|
| Parameters   | fine_tune_id(String)-The unique identifier of the fine-tuned model to be deleted. |
| Returns   | This method returns a `Single` object that contains the result of the delete operation. The `DeleteResult` object encapsulates the status of the deletion. |
| Return type   | `Single&lt;DeleteResult&gt;` |

<br>
> listFineTuneEvents

| Column Name | Content |
|-----------------|-----------------|
| Parameters   | fine_tune_id(String)-The ID of the fine-tuning process for which events are to be listed. |
| Returns   | This method returns a `Single` reactive type that wraps an `OpenAiResponse` object. The `OpenAiResponse` object contains a list of `FineTuneEvent` objects, each representing a fine-tuning event associated with the provided fine-tuning ID. |
| Return type   | `Single&lt;OpenAiResponse&lt;FineTuneEvent&gt;&gt;` |

<br>
> createChatCompletionStream

| Column Name | Content |
|-----------------|-----------------|
| Parameters   | request(ChatCompletionRequest)-The chat completion request object that contains the details of the chat completion to be created. |
| Returns   | This method returns a call object that can be used to communicate with the server in a streaming manner. The body of the response from the server will be a `ResponseBody` object. |
| Return type   | `Call&lt;ResponseBody&gt;` |

<br>
> createFineTune

| Column Name | Content |
|-----------------|-----------------|
| Parameters   | request(FineTuneRequest)-The request object containing the parameters for the fine-tuning job. |
| Returns   | This method returns a `Single` object that contains the result of the fine-tuning job creation. |
| Return type   | `Single&lt;FineTuneResult&gt;` |

<br>
> getEngine

| Column Name | Content |
|-----------------|-----------------|
| Parameters   | engine_id(String)-The unique identifier of the engine to be retrieved. |
| Returns   | This method returns a `Single` observable containing the `Engine` object that corresponds to the provided `engine_id`. |
| Return type   | `Single&lt;Engine&gt;` |

<br>
> getModel

| Column Name | Content |
|-----------------|-----------------|
| Parameters   | modelId(String)-The unique identifier of the model to be retrieved. |
| Returns   | This method returns a `Single&lt;Model&gt;` object, which represents the model retrieved from the OpenAI API. |
| Return type   | `Single&lt;Model&gt;` |

<br>
> createCompletion

| Column Name | Content |
|-----------------|-----------------|
| Parameters   | request(CompletionRequest)-The completion request object containing parameters for the OpenAI API. |
| Returns   | This method returns a `Single` observable containing the result of the completion request. The `CompletionResult` object includes the generated text and other information about the completion. |
| Return type   | `Single&lt;CompletionResult&gt;` |

<br>
> createEmbeddings

| Column Name | Content |
|-----------------|-----------------|
| Parameters   | request(EmbeddingRequest)-The request object containing the necessary information to create the embeddings. |
| Returns   | The method returns an instance of `Single&lt;EmbeddingResult&gt;`. This is a representation of the result of the embedding creation operation. |
| Return type   | `Single&lt;EmbeddingResult&gt;` |

<br>
> listFineTuningJobEvents

| Column Name | Content |
|-----------------|-----------------|
| Parameters   | fineTuningJobId(String)-The ID of the fine-tuning job whose events are to be listed. |
| Returns   | This method returns a `Single` object that wraps an `OpenAiResponse` object. The `OpenAiResponse` object contains a list of `FineTuningEvent` objects, each representing an event associated with the specified fine-tuning job. |
| Return type   | `Single&lt;OpenAiResponse&lt;FineTuningEvent&gt;&gt;` |

<br>
> billingUsage

| Column Name | Content |
|-----------------|-----------------|
| Parameters   | starDate(LocalDate)-The start date for the period for which the billing usage is to be fetched.
endDate(LocalDate)-The end date for the period for which the billing usage is to be fetched. |
| Returns   | This method returns the consumption amount information for the specified period. |
| Return type   | `Single&lt;BillingUsage&gt;` |

<br>
> createCompletionStream

| Column Name | Content |
|-----------------|-----------------|
| Parameters   | request(CompletionRequest)-The completion request to be processed. |
| Returns   | This method returns a `Call` object that contains the response body of the completion request. |
| Return type   | `Call&lt;ResponseBody&gt;` |
