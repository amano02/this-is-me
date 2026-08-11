"""
既存の静的サイト（this-is-me-main/1-6/img 以下の画像とindex.htmlの内容）を
DBへ初期投入するための管理コマンド。

使い方:
    python manage.py seed_initial_data
"""

from datetime import date
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.core.models import HeroSlide, SiteProfile
from apps.works.models import Genre, Work, WorkMedia, WorkTool

IMG_DIR = Path(settings.BASE_DIR) / "static" / "1-6" / "img"

GENRES = [
    {
        "name": "illustration",
        "display_order": 1,
        "background_image": "bg_03.jpg",
        "works": [
            ("01.jpg", "立ち絵１", 1),
            ("02.jpg", "アイコン", 2),
            ("03.jpg", "水彩画風", 3),
            ("04.jpg", "立ち絵２", 4),
            ("06.jpg", "一枚絵", 5),
        ],
    },
    {
        "name": "3dcg",
        "display_order": 2,
        "background_image": "bg_04.jpg",
        "works": [
            ("07.jpg", "パンケーキとミルク", 1),
            ("08.jpg", "キャラモデリング練習", 2),
            ("09.jpg", "コーヒー", 3),
            ("10.jpg", "バレンタイン", 4),
            ("11.jpg", "巳年", 5),
            ("12.jpg", "リソッド化", 6),
        ],
    },
    {
        "name": "music",
        "display_order": 3,
        "background_image": "bg_05.jpg",
        "works": [],
    },
    {
        "name": "others",
        "display_order": 4,
        "background_image": "bg_06.jpg",
        "works": [
            ("13.jpg", "名刺デザイン01", 1),
            ("14.jpg", "名刺デザイン02", 2),
            ("15.jpg", "名刺デザイン03", 3),
            ("16.jpg", "名刺デザイン04", 4),
            ("17.jpg", "ポスター１", 5),
            ("18.jpg", "ポスター２", 6),
            ("19.jpg", "アプリアイコン", 7),
            ("20.jpg", "文字デザイン", 8),
            ("21.jpg", "しおり表紙", 9),
            ("22.jpg", "グラフィックデザイン", 10),
        ],
    },
]

# 名刺デザイン01のみ、元のHTMLに詳細解説が残っていたため引き継ぐ
DETAILED_WORK_DESCRIPTIONS = {
    "名刺デザイン01": {
        "description": (
            "ここに作品のこだわりポイントや解説文を書きます。\n"
            "シンプルな配色の中に、視線を誘導する工夫を施しました。\n"
            "文字のカーニング（間隔）にもこだわり、洗練された印象を与えています。"
        ),
        "highlights": "ロゴの配置バランス\n紙の質感を生かした余白",
        "production_hours": 5,
        "tool": "Illustrator",
    }
}

HERO_SLIDES = [
    ("bg_01.jpg", "bg_sp01.jpg"),
    ("bg_02.jpg", "bg_sp02.jpg"),
    ("bg_03.jpg", "bg_sp04.jpg"),
]


class Command(BaseCommand):
    help = "既存の静的サイトのデータ（プロフィール・ジャンル・作品・ヒーロー画像）をDBへ初期投入します。"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="既にデータが存在していても再投入する（重複が作られる可能性があります）",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if not IMG_DIR.exists():
            self.stderr.write(self.style.ERROR(f"画像ディレクトリが見つかりません: {IMG_DIR}"))
            return

        if Work.objects.exists() and not options["force"]:
            self.stdout.write(
                self.style.WARNING(
                    "既に作品データが存在するため処理をスキップしました。"
                    "強制的に再投入する場合は --force を指定してください。"
                )
            )
            return

        self._seed_profile()
        self._seed_hero_slides()
        self._seed_genres_and_works()

        self.stdout.write(self.style.SUCCESS("初期データの投入が完了しました。"))

    def _open_file(self, filename):
        path = IMG_DIR / filename
        if not path.exists():
            self.stderr.write(self.style.WARNING(f"画像が見つかりません: {path}"))
            return None
        return File(open(path, "rb"), name=filename)

    def _seed_profile(self):
        if SiteProfile.objects.exists():
            self.stdout.write("サイトプロフィールは既に存在するためスキップしました。")
            return

        SiteProfile.objects.create(
            display_name="Hiroka Amano",
            role_title="multi creator",
            birth_place="shizuoka",
            birthday=date(2007, 2, 27),
            school="ZEN大学、dowango情報工科学院",
            bio="",
        )
        self.stdout.write(self.style.SUCCESS("サイトプロフィールを作成しました。"))

    def _seed_hero_slides(self):
        if HeroSlide.objects.exists():
            self.stdout.write("ヒーロースライドは既に存在するためスキップしました。")
            return

        for order, (pc_name, sp_name) in enumerate(HERO_SLIDES, start=1):
            pc_file = self._open_file(pc_name)
            sp_file = self._open_file(sp_name)
            if not pc_file:
                continue
            slide = HeroSlide(display_order=order, caption=f"Slide {order}")
            slide.image_pc.save(pc_name, pc_file, save=False)
            if sp_file:
                slide.image_sp.save(sp_name, sp_file, save=False)
            slide.save()
        self.stdout.write(self.style.SUCCESS("ヒーロースライドを作成しました。"))

    def _seed_genres_and_works(self):
        for genre_data in GENRES:
            genre, _ = Genre.objects.get_or_create(
                name=genre_data["name"],
                defaults={"display_order": genre_data["display_order"]},
            )
            bg_file = self._open_file(genre_data["background_image"])
            if bg_file and not genre.background_image:
                genre.background_image.save(
                    genre_data["background_image"], bg_file, save=False
                )
                genre.save()

            for image_name, title, order in genre_data["works"]:
                if Work.objects.filter(title=title).exists():
                    continue

                extra = DETAILED_WORK_DESCRIPTIONS.get(title, {})
                work = Work.objects.create(
                    genre=genre,
                    title=title,
                    description=extra.get("description", ""),
                    highlights=extra.get("highlights", ""),
                    production_hours=extra.get("production_hours"),
                    display_order=order,
                    status=Work.Status.PUBLISHED,
                )
                if extra.get("tool"):
                    tool, _ = WorkTool.objects.get_or_create(name=extra["tool"])
                    work.tools.add(tool)

                image_file = self._open_file(image_name)
                if image_file:
                    media = WorkMedia(
                        work=work,
                        media_type=WorkMedia.MediaType.IMAGE,
                        caption=title,
                        is_primary=True,
                        display_order=1,
                    )
                    media.file.save(image_name, image_file, save=True)

            self.stdout.write(self.style.SUCCESS(f"ジャンル『{genre.name}』の作品を作成しました。"))
