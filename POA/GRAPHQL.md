GraphQL is a query language for APIs that allows clients to request only the data they need, making it highly efficient and flexible. From a backend developer’s perspective, here’s how GraphQL works:

### 1. **Defining the Schema**

- **Schema**: The core of a GraphQL API is the schema, which defines the types of data the API can return, how these types are related, and the operations that can be performed on the data.
- A GraphQL schema consists of:

  - **Types**: Define the structure of the data (e.g., `User`, `Post`, `Comment`).
  - **Queries**: Define what data can be fetched (e.g., `getUser`, `listPosts`).
  - **Mutations**: Define operations that change data (e.g., `createUser`, `updatePost`).
  - **Subscriptions**: For real-time data (e.g., updates when data changes).

  Example schema:

  ```graphql
  type User {
    id: ID!
    name: String!
    posts: [Post!]
  }

  type Post {
    id: ID!
    title: String!
    author: User!
  }

  type Query {
    getUser(id: ID!): User
    listPosts: [Post]
  }

  type Mutation {
    createUser(name: String!): User
    createPost(title: String!, authorId: ID!): Post
  }
  ```

### 2. **Making Requests**

- **Queries**: Clients send GraphQL queries to the server, specifying exactly what data they need. The server responds with the requested data in the exact shape asked for by the client.

  - For example, a client could request the `name` and `posts` for a `User`, and the server only returns those fields:
    ```graphql
    query {
      getUser(id: "1") {
        name
        posts {
          title
        }
      }
    }
    ```

- **Mutations**: These are used to modify data. Mutations can also request a specific set of fields to be returned after performing the operation:
  ```graphql
  mutation {
    createPost(title: "GraphQL Introduction", authorId: "1") {
      id
      title
    }
  }
  ```

### 3. **Resolvers**

- **Resolvers** are functions on the backend that define how to fetch or manipulate the data for each field in the schema.
- Each field in a GraphQL schema has a corresponding resolver. Resolvers can fetch data from databases, third-party APIs, or other services.

For example, the resolver for `getUser` would fetch a user by ID:

```javascript
const resolvers = {
  Query: {
    getUser: (parent, args, context, info) => {
      return context.db.getUserById(args.id);
    },
  },
  Mutation: {
    createUser: (parent, args, context, info) => {
      return context.db.createUser(args.name);
    },
  },
};
```

- Resolvers can be nested. For example, the `posts` field of the `User` type may call another resolver to get the user's posts:
  ```javascript
  const resolvers = {
    User: {
      posts: (user, args, context) => {
        return context.db.getPostsByUserId(user.id);
      },
    },
  };
  ```

### 4. **Data Fetching and Efficiency**

- Unlike REST, where clients often receive large amounts of unnecessary data or need multiple requests to get related data, GraphQL allows clients to:
  - **Request only what they need**: This avoids over-fetching (getting too much data) or under-fetching (requiring additional API calls to get related data).
  - **Batch requests**: Clients can get all related data in one query rather than multiple REST calls.

Example of fetching nested data in one request:

```graphql
query {
  getUser(id: "1") {
    name
    posts {
      title
    }
  }
}
```

### 5. **Mutations and Data Modification**

- Mutations allow clients to modify data (like POST, PUT, DELETE in REST).
- After performing the mutation, GraphQL can return a specified set of fields for the newly created/modified resource.

Example:

```graphql
mutation {
  createPost(title: "GraphQL Deep Dive", authorId: "1") {
    id
    title
  }
}
```

### 6. **Subscriptions for Real-Time Updates**

- **Subscriptions** are used for real-time functionality. When a mutation changes data that a client is interested in, the server sends the update to the subscribed client.
- This is useful in scenarios like messaging apps, where users need real-time updates without constantly polling the server.

Example subscription:

```graphql
subscription {
  postCreated {
    id
    title
  }
}
```

### 7. **Client-Side Flexibility**

- The client (e.g., web app, mobile app) defines the structure of the response. If the client only needs part of the data, it can specify exactly which fields to retrieve.
- **No versioning**: GraphQL eliminates the need for versioning APIs (e.g., `/v1/users`, `/v2/users` in REST) because the client requests only what it needs, even as the API evolves.

### 8. **Error Handling**

- GraphQL allows partial success, meaning that if part of a query fails, the server will still return the successful parts, along with error information for the failed parts.

Example error response:

```json
{
  "data": {
    "getUser": null
  },
  "errors": [
    {
      "message": "User not found",
      "locations": [{ "line": 2, "column": 3 }],
      "path": ["getUser"]
    }
  ]
}
```

### 9. **Authentication and Authorization**

- **Context**: Authentication tokens (like JWT) are usually passed to the GraphQL server via HTTP headers. The backend uses this context to validate the user and control access to data.
- **Authorization**: The resolvers can include logic to determine whether the user has the necessary permissions to perform an action or access data.

Example of passing an authenticated user in the context:

```javascript
const server = new ApolloServer({
  typeDefs,
  resolvers,
  context: ({ req }) => {
    const token = req.headers.authorization || "";
    const user = getUserFromToken(token);
    return { user };
  },
});
```

### 10. **Tools and Libraries**

- **Apollo Server** (Node.js): Popular GraphQL server implementation.
- **GraphQL.js**: Official reference implementation of a GraphQL server.
- **Prisma**: Database ORM tool that works well with GraphQL.
- **Relay**: A GraphQL client designed to work with React, useful for building complex front-end applications.

### Summary

In GraphQL, the **client controls** what data it wants through flexible queries. The **backend defines the schema** and provides resolvers to fetch or manipulate data. This allows for efficient data retrieval, fine-grained control over responses, and simpler API evolution.
