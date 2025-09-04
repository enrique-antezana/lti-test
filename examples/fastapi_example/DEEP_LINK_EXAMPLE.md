# Rick and Morty Deep Link Example

This example demonstrates how to create LTI 1.3 deep links using PyLTI1p3 with FastAPI. The example fetches characters from the Rick and Morty API and allows users to create deep links for selected characters.

## Features

- **Character Selection Interface**: A web interface that displays the first 5 characters from the Rick and Morty API
- **Deep Link Generation**: Creates LTI deep links for selected characters
- **Character Detail Pages**: Individual pages for each character with full details
- **LTI Integration**: Proper LTI 1.3 deep link response handling

## How It Works

### 1. Deep Link Launch

When an LTI platform initiates a deep link launch:

- The `/api/launch` endpoint detects it's a deep link launch
- Redirects to `/character-selection` page

### 2. Character Selection

The character selection page:

- Fetches the first 5 characters from `https://rickandmortyapi.com/api/character/1` through `/api/character/5`
- Displays them in an interactive card interface
- Allows users to select which characters to create deep links for

### 3. Deep Link Creation

When users submit their selection:

- The `/api/character-selection` POST endpoint processes the selection
- Creates `DeepLinkResource` objects for each selected character
- Generates a proper LTI deep link response using PyLTI1p3's `DeepLink` class
- Returns the response as HTML that automatically submits back to the LMS

### 4. Character Detail Pages

Each deep link points to `/character-detail/{character_id}` which:

- Fetches the full character data from the Rick and Morty API
- Displays a detailed character information page

## API Endpoints

- `GET /api/characters` - Fetches first 5 characters from Rick and Morty API
- `GET /character-selection` - Character selection interface
- `POST /api/character-selection` - Handles deep link creation
- `GET /character-detail/{character_id}` - Character detail page
- `GET /api/launch` - LTI launch endpoint (handles both resource and deep link launches)

## Character Data Structure

Each character includes:

- `id`: Character ID
- `name`: Character name
- `status`: Alive/Dead/Unknown
- `species`: Character species
- `gender`: Character gender
- `origin`: Origin location
- `location`: Current location
- `image`: Character image URL
- `episode`: List of episode URLs
- `url`: API URL for the character

## Deep Link Resources

Each deep link resource includes:

- **Title**: "Rick and Morty Character: {character_name}"
- **URL**: Points to the character detail page
- **Icon**: Character image
- **Custom Parameters**:
  - `character_id`: Character ID
  - `character_name`: Character name
  - `character_status`: Character status
  - `character_species`: Character species

## Usage

1. Configure your LTI platform to use this tool for deep linking
2. Launch the tool from your LMS
3. Select characters you want to create deep links for
4. Click "Create Deep Links for Selected Characters"
5. The deep links will be created and submitted back to the LMS
6. Users can then access individual character pages through the created deep links

## Dependencies

- `httpx`: For making HTTP requests to the Rick and Morty API
- `pylti1p3`: For LTI 1.3 functionality
- `fastapi`: Web framework
- `jinja2`: Template engine

## Example Character IDs

The example uses characters 1-5 from the Rick and Morty API:

1. Rick Sanchez
2. Morty Smith
3. Summer Smith
4. Beth Smith
5. Jerry Smith

You can modify the character IDs in the code to use different characters or fetch more characters as needed.
