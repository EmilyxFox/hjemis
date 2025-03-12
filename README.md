# Hjem-IS

Hjem-IS is the company that runs ice-cream vans in Denmark (and Norway, although this integration only supports Denmark so far). This integration uses their API to look fetch upcoming ice-cream van visits near you.

## Sensor

| Field     | Description                                                                           |
| --------- | ------------------------------------------------------------------------------------- |
| **State** | A timestamp to when the next visit is. This state will show as a countdown in the UI. |
| Address   | The address for the stop. The van stops at redetermined locations.                    |
| Distance  | How far this stop is from your home                                                   |

## Installation

### HACS installation

1. Go to HACS, click on `Integrations`
2. Click on the 3 dots in the top corner `⋮` and select `Custom repositories`
3. Add `https://github.com/emilyxfox/hjemis`, and select `integration` as the `Category`, then click add.
4. Restart Home Assistant when prompted.
5. Go to `Configuration` -> `Integrations`, click `+` and search for `HjemIS`.
6. Your home coordinates should already be prefilled, but you can change them if you want to.

### Manual installation

1. Create a `custom_components` folder in your Home Assistant folder if it doesn't already exist.
2. Put the `custom_components/hjemis` (from this repo) folder in your `custom_components` folder.
3. Restart Home Assistant.
4. Go to `Configuration` -> `Integrations`, click `+` and search for `HjemIS`.
5. Your home coordinates should already be prefilled, but you can change them if you want to.
