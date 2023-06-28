export const actions = [
  {
    "_id": "63856fa8f7f9db28bcddf0f5",
    "name": "procurement",
    "upstream": [],
    "downstream": [
      {
        "node_type": "Material",
        "node_id": "63856fa8f7f9db28bcddf0f4"
      }
    ],
    "tags": [],
    "actor_id": "63856fa8f7f9db28bcddf0f3",
    "ingredients": [],
    "created_at": "2022-11-28T18:34:16.703000",
    "updated_at": "2022-11-28T18:34:16.703000"
  },
  {
    "_id": "63856fa8f7f9db28bcddf0f6",
    "name": "grind",
    "upstream": [
      {
        "node_type": "Material",
        "node_id": "63856fa8f7f9db28bcddf0f4"
      }
    ],
    "downstream": [
      {
        "node_type": "Material",
        "node_id": "63856fa8f7f9db28bcddf0fa"
      }
    ],
    "tags": [],
    "actor_id": "63856fa8f7f9db28bcddf0f3",
    "ingredients": [
      {
        "name": "Titanium Dioxide",
        "material_id": "63856fa8f7f9db28bcddf0f4",
        "amount": 100,
        "unit": "percent"
      }
    ],
    "created_at": "2022-11-28T18:34:16.988000",
    "updated_at": "2022-11-28T18:34:16.988000"
  },
  {
    "_id": "63856fa8f7f9db28bcddf0f7",
    "name": "sinter",
    "upstream": [
      {
        "node_type": "Material",
        "node_id": "63856fa8f7f9db28bcddf0fa"
      }
    ],
    "downstream": [
      {
        "node_type": "Material",
        "node_id": "63856fa8f7f9db28bcddf0fb"
      }
    ],
    "tags": [],
    "actor_id": "63856fa8f7f9db28bcddf0f3",
    "ingredients": [
      {
        "name": "Titanium Dioxide - grind",
        "material_id": "63856fa8f7f9db28bcddf0fa",
        "amount": 100,
        "unit": "percent"
      }
    ],
    "created_at": "2022-11-28T18:34:16.990000",
    "updated_at": "2022-11-28T18:34:16.990000"
  },
  {
    "_id": "63856fa8f7f9db28bcddf0f8",
    "name": "grind",
    "upstream": [
      {
        "node_type": "Material",
        "node_id": "63856fa8f7f9db28bcddf0fb"
      }
    ],
    "downstream": [
      {
        "node_type": "Material",
        "node_id": "63856fa8f7f9db28bcddf0fc"
      }
    ],
    "tags": [],
    "actor_id": "63856fa8f7f9db28bcddf0f3",
    "final_step": true,
    "ingredients": [
      {
        "name": "Titanium Dioxide - grind - sinter",
        "material_id": "63856fa8f7f9db28bcddf0fb",
        "amount": 100,
        "unit": "percent"
      }
    ],
    "created_at": "2022-11-28T18:34:16.993000",
    "updated_at": "2022-11-28T18:34:16.993000"
  },
  {
    "_id": "63b4846259d804bbe41fba20",
    "name": "procurement",
    "upstream": [],
    "downstream": [
      {
        "node_type": "Material",
        "node_id": "63b4846259d804bbe41fba1f"
      }
    ],
    "tags": [],
    "actor_id": "63b4846059d804bbe41fba15",
    "ingredients": [],
    "created_at": "2023-01-03T11:39:17.272000",
    "updated_at": "2023-01-03T11:39:17.272000"
  },
  {
    "_id": "63b4846259d804bbe41fba21",
    "name": "grind",
    "upstream": [
      {
        "node_type": "Material",
        "node_id": "63b4846259d804bbe41fba1f"
      }
    ],
    "downstream": [
      {
        "node_type": "Material",
        "node_id": "63b4846259d804bbe41fba22"
      }
    ],
    "tags": [],
    "actor_id": "63b4846059d804bbe41fba15",
    "ingredients": [
      {
        "name": "Titanium Dioxide",
        "material_id": "63b4846259d804bbe41fba1f",
        "amount": 1,
        "unit": "g"
      }
    ],
    "created_at": "2023-01-03T11:39:17.279000",
    "updated_at": "2023-01-03T11:39:17.279000"
  },
  {
    "_id": "63b4846259d804bbe41fba23",
    "name": "sinter",
    "upstream": [
      {
        "node_type": "Material",
        "node_id": "63b4846259d804bbe41fba22"
      }
    ],
    "downstream": [
      {
        "node_type": "Material",
        "node_id": "63b4846259d804bbe41fba24"
      }
    ],
    "tags": [],
    "actor_id": "63b4846059d804bbe41fba13",
    "ingredients": [
      {
        "name": "Titanium Dioxide - grind",
        "material_id": "63b4846259d804bbe41fba22",
        "amount": 100,
        "unit": "percent"
      }
    ],
    "created_at": "2023-01-03T11:39:17.280000",
    "updated_at": "2023-01-03T11:39:17.280000"
  },
  {
    "_id": "63b4846259d804bbe41fba25",
    "name": "grind",
    "upstream": [
      {
        "node_type": "Material",
        "node_id": "63b4846259d804bbe41fba24"
      }
    ],
    "downstream": [
      {
        "node_type": "Material",
        "node_id": "63b4846259d804bbe41fba26"
      }
    ],
    "tags": [],
    "actor_id": "63b4846059d804bbe41fba15",
    "final_step": true,
    "ingredients": [
      {
        "name": "Titanium Dioxide - grind - sinter",
        "material_id": "63b4846259d804bbe41fba24",
        "amount": 100,
        "unit": "percent"
      }
    ],
    "created_at": "2023-01-03T11:39:17.285000",
    "updated_at": "2023-01-03T11:39:17.285000"
  },
  {
    "_id": "63b4846759d804bbe41fba80",
    "name": "procurement",
    "upstream": [],
    "downstream": [
      {
        "node_type": "Material",
        "node_id": "63b4846759d804bbe41fba7f"
      }
    ],
    "tags": [],
    "actor_id": "63b4846059d804bbe41fba15",
    "ingredients": [],
    "created_at": "2023-01-03T11:39:20.599000",
    "updated_at": "2023-01-03T11:39:20.599000"
  },
  {
    "_id": "63b4846759d804bbe41fba81",
    "name": "grind",
    "upstream": [
      {
        "node_type": "Material",
        "node_id": "63b4846759d804bbe41fba7f"
      }
    ],
    "downstream": [
      {
        "node_type": "Material",
        "node_id": "63b4846859d804bbe41fba85"
      }
    ],
    "tags": [],
    "actor_id": "63b4846059d804bbe41fba15",
    "ingredients": [
      {
        "name": "Titanium Dioxide",
        "material_id": "63b4846759d804bbe41fba7f",
        "amount": 100,
        "unit": "percent"
      }
    ],
    "created_at": "2023-01-03T11:39:20.604000",
    "updated_at": "2023-01-03T11:39:20.604000"
  },
  {
    "_id": "63b4846759d804bbe41fba82",
    "name": "sinter",
    "upstream": [
      {
        "node_type": "Material",
        "node_id": "63b4846859d804bbe41fba85"
      }
    ],
    "downstream": [
      {
        "node_type": "Material",
        "node_id": "63b4846859d804bbe41fba86"
      }
    ],
    "tags": [],
    "actor_id": "63b4846059d804bbe41fba13",
    "ingredients": [
      {
        "name": "Titanium Dioxide - grind",
        "material_id": "63b4846859d804bbe41fba85",
        "amount": 100,
        "unit": "percent"
      }
    ],
    "created_at": "2023-01-03T11:39:20.608000",
    "updated_at": "2023-01-03T11:39:20.608000"
  },
  {
    "_id": "63b4846759d804bbe41fba83",
    "name": "grind",
    "upstream": [
      {
        "node_type": "Material",
        "node_id": "63b4846859d804bbe41fba86"
      }
    ],
    "downstream": [
      {
        "node_type": "Material",
        "node_id": "63b4846859d804bbe41fba87"
      }
    ],
    "tags": [],
    "actor_id": "63b4846059d804bbe41fba15",
    "final_step": true,
    "ingredients": [
      {
        "name": "Titanium Dioxide - grind - sinter",
        "material_id": "63b4846859d804bbe41fba86",
        "amount": 100,
        "unit": "percent"
      }
    ],
    "created_at": "2023-01-03T11:39:20.612000",
    "updated_at": "2023-01-03T11:39:20.612000"
  },
  {
    "_id": "63b484a259d804bbe41fba97",
    "name": "procurement",
    "upstream": [],
    "downstream": [
      {
        "node_type": "Material",
        "node_id": "63b484a259d804bbe41fba96"
      }
    ],
    "tags": [],
    "actor_id": "63856fa8f7f9db28bcddf0f3",
    "supplier": "Alfa Aesar",
    "CAS_number": "13463-67-7",
    "price": "$100/gram",
    "ingredients": [],
    "created_at": "2023-01-03T11:40:19.004000",
    "updated_at": "2023-01-03T11:40:19.004000"
  },
  {
    "_id": "63b484a259d804bbe41fba99",
    "name": "procurement",
    "upstream": [],
    "downstream": [
      {
        "node_type": "Material",
        "node_id": "63b484a259d804bbe41fba98"
      }
    ],
    "tags": [],
    "actor_id": "63856fa8f7f9db28bcddf0f3",
    "supplier": "Alfa Aesar",
    "CAS_number": "1303-96-4",
    "price": "$100/gram",
    "ingredients": [],
    "created_at": "2023-01-03T11:40:19.007000",
    "updated_at": "2023-01-03T11:40:19.007000"
  },
  {
    "_id": "63b484a659d804bbe41fbaa3",
    "name": "grind",
    "upstream": [
      {
        "node_type": "Material",
        "node_id": "63b484a259d804bbe41fba96"
      },
      {
        "node_type": "Material",
        "node_id": "63b484a259d804bbe41fba98"
      }
    ],
    "downstream": [
      {
        "node_type": "Material",
        "node_id": "63b484a659d804bbe41fbaa7"
      }
    ],
    "tags": [],
    "actor_id": "63856fa8f7f9db28bcddf0f3",
    "instrument": "mortar and pestle",
    "duration": "1 hour",
    "ingredients": [
      {
        "name": "Titanium Dioxide",
        "material_id": "63b484a259d804bbe41fba96",
        "amount": 1,
        "unit": "g"
      },
      {
        "name": "Bismuth Oxide",
        "material_id": "63b484a259d804bbe41fba98",
        "amount": 2,
        "unit": "g"
      }
    ],
    "created_at": "2023-01-03T11:40:24.751000",
    "updated_at": "2023-01-03T11:40:24.751000"
  },
  {
    "_id": "63b484a659d804bbe41fbaa4",
    "name": "sinter",
    "upstream": [
      {
        "node_type": "Material",
        "node_id": "63b484a659d804bbe41fbaa7"
      }
    ],
    "downstream": [
      {
        "node_type": "Material",
        "node_id": "63b484a659d804bbe41fbaa8"
      }
    ],
    "tags": [],
    "actor_id": "63b4846059d804bbe41fba13",
    "temperature_celsius": 1000,
    "duration_hours": 4,
    "ingredients": [
      {
        "name": "Titanium Dioxide+Bismuth Oxide - grind",
        "material_id": "63b484a659d804bbe41fbaa7",
        "amount": 100,
        "unit": "percent"
      }
    ],
    "created_at": "2023-01-03T11:40:24.752000",
    "updated_at": "2023-01-03T11:40:24.752000"
  },
  {
    "_id": "63b484a659d804bbe41fbaa5",
    "name": "grind",
    "upstream": [
      {
        "node_type": "Material",
        "node_id": "63b484a659d804bbe41fbaa8"
      }
    ],
    "downstream": [
      {
        "node_type": "Material",
        "node_id": "63b484a659d804bbe41fbaa9"
      }
    ],
    "tags": [],
    "actor_id": "63856fa8f7f9db28bcddf0f3",
    "final_step": true,
    "instrument": "mortar and pestle",
    "duration": "1 hour",
    "ingredients": [
      {
        "name": "Titanium Dioxide+Bismuth Oxide - grind - sinter",
        "material_id": "63b484a659d804bbe41fbaa8",
        "amount": 100,
        "unit": "percent"
      }
    ],
    "created_at": "2023-01-03T11:40:24.753000",
    "updated_at": "2023-01-03T11:40:24.753000"
  }
]