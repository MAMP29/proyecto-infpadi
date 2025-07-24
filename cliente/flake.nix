{
  description = "Flake de desarrollo para el cliente";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
  };

  outputs = { self, nixpkgs }: let
      system = "x86_64-linux";
      pkgs = import nixpkgs {
        inherit system;
      };

    in {
      devShells.${system}.default = pkgs.mkShell {
        buildInputs = [
          pkgs.nodejs_22
          pkgs.zsh
        ];

        shellHook = ''
          echo "Entorno de nodejs preparado"
        '';
        };
    };


  }
