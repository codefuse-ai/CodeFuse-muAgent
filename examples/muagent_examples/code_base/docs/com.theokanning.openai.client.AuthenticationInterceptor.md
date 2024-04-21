
> com.theokanning.openai.client.AuthenticationInterceptor

Bases: Interceptor from okhttp3 package

The AuthenticationInterceptor class is an OkHttp Interceptor that adds an authorization token header to the request.

token(String)-The authorization token that will be added to the header of the request.

<br>
> intercept

| Column Name | Content |
|-----------------|-----------------|
| Parameters   | chain(Chain)-The chain of interceptors that the current interceptor is part of. |
| Returns   | The method returns the response received after the request has been processed by the chain of interceptors. |
| Return type   | Response |
