"""
Django development guidelines and best practices.
"""

# Best Practices for Development

## Models
- Use descriptive field names that reflect business logic
- Always include verbose_name and help_text on fields
- Create custom managers for complex querysets
- Use model Meta class for ordering and permissions

## Migrations
- Test migrations in development before deploying
- Always review migration files before committing
- Use --fake-initial for initial migrations on existing databases
- Keep migrations small and focused

## Views
- Use class-based views (CBVs) for consistency
- Keep views thin; put business logic in models/services
- Always validate user input
- Use Django's built-in permission decorators

## Testing
- Aim for 80%+ code coverage
- Write tests before implementing features (TDD)
- Test edge cases and error conditions
- Use fixtures for test data

## Security
- Always use CSRF protection for forms
- Validate and sanitize all user input
- Use parameterized queries to prevent SQL injection
- Store sensitive data in environment variables
- Use Django's authentication system

## Performance
- Use select_related() for ForeignKey and OneToOneField
- Use prefetch_related() for ManyToManyField and reverse relations
- Index frequently queried fields
- Cache expensive queries
- Use database transactions for related updates
