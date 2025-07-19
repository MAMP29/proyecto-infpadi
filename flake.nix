{
  description = "A very basic flake";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
  };

  outputs = { self, nixpkgs }: let
    system = "x86_64-linux";
    pkgs = import nixpkgs {
      inherit system;
      config. allowUnfree = true;
    };
    pythonEnv = pkgs.python313.withPackages (ps: with ps; [
      torch-bin
      torchvision-bin
      numpy
      fastapi
      uvicorn
      ray
      onnx
      onnxruntime
      grpcio
      python-multipart
    ]);

  in {
    devShells.${system}.default = pkgs.mkShell {
      buildInputs = [
        pythonEnv
        pkgs.zsh
        pkgs.grpc
      ];

      shellHook = ''
        echo "Entorno preparado"
        exec zsh
      '';
    };
  };
}
